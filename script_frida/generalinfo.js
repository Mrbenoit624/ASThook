function android_appInfo(){
    var res;
    Java.performNow(function () {
        // https://developer.android.com/reference/android/os/Build.html
        const Build = Java.use('android.os.Build');
    
        const ActivityThread = Java.use('android.app.ActivityThread');
    
        var currentApplication = ActivityThread.currentApplication();
        var context = currentApplication.getApplicationContext();
    
        res = {
            application_name: context.getPackageName(),
            filesDirectory: context.getFilesDir().getAbsolutePath().toString(),
            cacheDirectory: context.getCacheDir().getAbsolutePath().toString(),
            externalCacheDirectory: context.getExternalCacheDir().getAbsolutePath().toString(),
            codeCacheDirectory: context.getCodeCacheDir().getAbsolutePath().toString(),
            obbDir: context.getObbDir().getAbsolutePath().toString(),
            packageCodePath: context.getPackageCodePath().toString()
        };
    })
    
    return res
}
send(android_appInfo());
