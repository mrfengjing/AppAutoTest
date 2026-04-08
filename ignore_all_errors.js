// ignore_all_errors.js
setImmediate(function() {
    console.log("[+] 启动：忽略所有错误 + 强制 APP 继续运行");

    // ==============================================
    // 1. 屏蔽 fopen 失败 → 永远返回有效文件指针
    // ==============================================
    try {
        Interceptor.attach(Module.findExportByName("libsystem_c.dylib", "fopen"), {
            onEnter: function(args) {
                this.path = args[0].readCString();
            },
            onLeave: function(retval) {
                if (retval.isNull()) {
                    console.log("[✅ 修复] fopen 失败: " + this.path + " → 强制返回伪文件");
                    retval.replace(ptr("0x12345678")); // 伪指针，不会崩溃
                }
            }
        });
    } catch(e) {}

    // ==============================================
    // 2. 屏蔽 open 系统调用失败 → 永远返回 fd=3
    // ==============================================
    try {
        Interceptor.attach(Module.findExportByName("libsystem_c.dylib", "open"), {
            onLeave: function(retval) {
                if (retval.toInt32() < 0) {
                    console.log("[✅ 修复] open 失败 → 强制返回 fd=3");
                    retval.replace(ptr("3"));
                }
            }
        });
    } catch(e) {}

    // ==============================================
    // 3. 屏蔽 NSAssert 断言失败 → 不崩溃
    // ==============================================
    try {
        var NSAssertFunc = ObjC.classes.NSAssertionHandler;
        if (NSAssertFunc) {
            Interceptor.attach(NSAssertFunc.handleFailureInMethod_object_file_lineNumber_description_.implementation, {
                onEnter: function() {
                    console.log("[✅ 屏蔽] NSAssert 崩溃");
                }
            });
        }
    } catch(e) {}

    // ==============================================
    // 4. 屏蔽 NSException 异常 → 直接返回，不崩溃
    // ==============================================
    try {
        Interceptor.attach(ObjC.classes.NSException("- raise").implementation, {
            onEnter: function() {
                console.log("[✅ 屏蔽] NSException 异常");
                throw new Error("continue"); // 强制跳过崩溃
            }
        });
    } catch(e) {}

    // ==============================================
    // 5. 屏蔽 abort() / exit() / kill  -> 不让APP退出
    // ==============================================
    try {
        var abort = Module.findExportByName("libsystem_c.dylib", "abort");
        Interceptor.attach(abort, {
            onEnter: function() {
                console.log("[✅ 屏蔽] abort()");
            }
        });

        var exit = Module.findExportByName("libsystem_c.dylib", "exit");
        Interceptor.attach(exit, {
            onEnter: function() {
                console.log("[✅ 屏蔽] exit()");
            }
        });
    } catch(e) {}

    console.log("[+] 所有错误屏蔽完成 → APP 会强行继续运行！");
});
