if (ObjC.available) {
    const security = Module.load('/System/Library/Frameworks/Security.framework/Security');
    const SecItemCopyMatching = new NativeFunction(
        security.findExportByName('SecItemCopyMatching'),
        'int', ['pointer', 'pointer']
    );

    // 构造查询条件，获取所有钥匙串条目
    const kSecClass = ObjC.classes.NSMutableDictionary.alloc().init();
    kSecClass.setObject_forKey_(ObjC.classes.NSString.stringWithString_("genp"), ObjC.classes.NSString.stringWithString_("class"));
    kSecClass.setObject_forKey_(ObjC.classes.NSNumber.numberWithBool_(true), ObjC.classes.NSString.stringWithString_("returnAttributes"));
    kSecClass.setObject_forKey_(ObjC.classes.NSNumber.numberWithBool_(true), ObjC.classes.NSString.stringWithString_("returnData"));
    kSecClass.setObject_forKey_(ObjC.classes.NSString.stringWithString_("kSecMatchLimitAll"), ObjC.classes.NSString.stringWithString_("matchLimit"));

    const resultPtr = Memory.alloc(Process.pointerSize);
    const status = SecItemCopyMatching(kSecClass, resultPtr);

    if (status === 0) {
        const result = new ObjC.Object(Memory.readPointer(resultPtr));
        console.log(JSON.stringify(result, null, 2));
    } else {
        console.log("钥匙串查询失败，错误码：" + status);
    }
}
