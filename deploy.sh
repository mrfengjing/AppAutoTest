#!/bin/sh
IPA_PATH=$1
IPA_NAME=$(basename "$IPA_PATH")
PROVISION_PATH="provision/demo_dev.mobileprovision"
PROVISION_DECODED="provision/provision.plist"

#IDENTIFY="iPhone Distribution: Zhong qihong (X5BBR46R2Q)"
IDENTIFY="7A98965D9E9713CDAF26B9957D6ACC254FE34B97"
#BUNDLE_ID="com.demo2026.com"
if ! [ -f "$IPA_PATH" ]; then
  echo "文件不存在: $IPA_PATH"
  exit 1
fi

security cms -D -i "$PROVISION_PATH" >"$PROVISION_DECODED"
BUNDLE_ID=$(/usr/libexec/PlistBuddy -c "Print :Entitlements:application-identifier" "$PROVISION_DECODED" 2>/dev/null)
BUNDLE_ID=$(echo "$BUNDLE_ID" | awk -F '.' '{for(i=2;i<=NF;i++){printf("%s.",$i)};print ""}' | sed 's/.$//')

WORKPLACE="./workplace"
mkdir -p "$WORKPLACE"
cd "$WORKPLACE" || {
  echo "$WORKPLACE 不存在!"
  exit 1
}

echo "BUNDLE_ID: $BUNDLE_ID"
[ -f "$IPA_NAME" ] || {
  echo "cp $IPA_PATH ..."
  cp -v "$IPA_PATH" "$WORKPLACE"
}
echo "clean ..."
rm -rf Payload Payload.zip Payload.ipa _floatsignTemp
case "$IPA_NAME" in
*.ipa)
  echo "unzip $IPA_NAME ..."
  unzip -oq "$IPA_NAME" -d .
  find . -name "*.mobileprovision" -type f -exec echo "deleted {} " \; -exec rm -f {} \;
  #  find . -name "*.mobileprovision" -type f -delete
  #  zip -r -q "Payload.zip" "Payload/"
  #  echo "重签..."
  #  fastlane sigh resign "$IPA_NAME" --signing_identity "iPhone Distribution: Zhong qihong (X5BBR46R2Q)" --provisioning_profile "../$PROVISION"
  #  echo "重签完成!"
  #  mv "Payload.zip" "Payload.ipa"
  ;;
esac
find . -name "*.app" -type d 2>/dev/null | while read -r f; do
  INFO_PLIST="$f/Info.plist"
  echo "clean $f/PlugIns ..."
  rm -rf "$f/PlugIns"
  [ -f "$INFO_PLIST" ] && {
    echo "Old Bundle ID：$(/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" "$INFO_PLIST")"
    echo "Reset Bundle ID to $BUNDLE_ID ..."
    /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier $BUNDLE_ID" "$INFO_PLIST"
    echo "New Bundle ID：$(/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" "$INFO_PLIST")"
    cp "../$PROVISION_PATH" "$f/embedded.mobileprovision"
    APP_NAME=$(basename "$f" .app)
    ENTITLEMENTS_FILE="$APP_NAME.entitlements"
    echo "generate $ENTITLEMENTS_FILE ..."
    /usr/libexec/PlistBuddy -x -c "Print :Entitlements" "../$PROVISION_DECODED" > "$ENTITLEMENTS_FILE"
    find "$f" -name "*.dylib" -exec codesign --remove-signature {} \; 2>/dev/null || true
    find "$f/Frameworks" -name "*.framework" -exec codesign --remove-signature {} \; 2>/dev/null || true
    find "$f/Frameworks" -name "*.framework" -type d 2>/dev/null | while read -r fwk; do
      echo "重签 $fwk ..."
      codesign --force --sign "$IDENTIFY" "$fwk"
    done

    find "$f/Frameworks" -name "*.dylib" -type f 2>/dev/null | while read -r dylib; do
      echo "重签 $dylib ..."
      codesign --force --sign "$IDENTIFY" "$dylib"
    done
    echo "重签 $f ..."
    if [ -f "$ENTITLEMENTS_FILE" ]; then
      codesign --force --sign "$IDENTIFY" --entitlements "$ENTITLEMENTS_FILE" "$f"
    else
      codesign --force --sign "$IDENTIFY" "$f"
    fi
    echo "重签 $f 完成!"
    codesign --verify --verbos "$f"
    echo "zip Payload ..."
    zip -r -q "Payload.zip" "Payload/"
    echo "mv Payload.zip Payload.ipa ..."
    mv "Payload.zip" "Payload.ipa"
#    echo "重签 Payload.ipa ..."

    #    security find-identity -v -s codesigning
    #    codesign --force --sign "$IDENTIFY" "Payload.ipa" --preserve-metadata=identifier,entitlements,flags --timestamp=none
#    codesign --verify --verbos "Payload.ipa"
    #    echo "重签完成!"

    #    fastlane sigh resign "Payload.ipa" --signing_identity "$IDENTIFY" --provisioning_profile "../$PROVISION_PATH"
    #    echo "安装$f ......"
    #    ios-deploy --debug --bundle "$f"
  }
done
exit 0
case $DEPLOY_MODE in
1)
  # ipa 重签
  # 【1 security find-identity -v
  # 【2】xcrun security find-identity -v
  #  # 只看开发证书 (Apple Development / iPhone Developer)
  #security find-identity -v | grep -E "Apple Development|iPhone Developer"
  #  xcodebuild -showBuildSettings | grep CODE_SIGN_IDENTITY
  ## 只看分发证书 (Apple Distribution / iPhone Distribution)
  #  查看项目构建设置中可用的身份
  #security find-identity -v | grep -E "Apple Distribution|iPhone Distribution"
  PROVISION_FILES=$(find "$APP_DIR" -name "*.mobileprovision" -type f 2>/dev/null)

  echo "重签..."
  fastlane sigh resign "$IPA_NAME" --signing_identity "iPhone Distribution: Zhong qihong (X5BBR46R2Q)" --provisioning_profile "../$PROVISION"
  echo "重签完成!"

  # 提取 Bundle ID

  ;;
2) ;;
*)
  echo "未知操作类型"
  exit 1
  ;;
esac
exit 0
# 安装app到测试机
echo "安装app到测试机 ......"
ios-deploy --debug --bundle /Users/smwl/Library/Developer/Xcode/DerivedData/SMSDK-czxzzvlrnrphfxdfxtqkotwcntor/Build/Products/Debug-iphoneos/SMSDKDevApp.app

# 查看手机所有应用
echo "查看手机所有应用 ......"
ios-deploy --list_bundle_id

# 下载指定应用沙盒文件
echo "下载指定应用沙盒文件 ......"
ios-deploy --download=/ --bundle_id com.demo2026.com --to ./com.demo2026.com
# 上传文件到沙盒
# 下载DCIM中文件
echo "下载DCIM中文件 ......"
ios-deploy -f -w/
# 上传文件到DCIM
