
//Java.perform(function()
//  {
//    FileInputStream : Java.use("java.io.FileInputStream");
//    FileInputStream.new[0].overload('java.lang.String').implementation = function (str)
//    {
//      send(str);
//      return FileInputStream.new[0].call(this, a0);
//    }
//  });

Interceptor.attach(Module.findExportByName("libc.so" , "open"), {
    onEnter: function(args) {
      var path = Memory.readCString(ptr(args[0]));
      if ( !path.startsWith("/dev") && !path.startsWith("/sys"))
        send("open("+ path + "," + args[1] + ")");
    },
    onLeave:function(retval){
    }
});
