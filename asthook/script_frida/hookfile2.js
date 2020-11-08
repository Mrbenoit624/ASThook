
//Java.perform(function()
//  {
//    FileInputStream : Java.use("java.io.FileInputStream");
//    FileInputStream.new[0].overload('java.lang.String').implementation = function (str)
//    {
//      send(str);
//      return FileInputStream.new[0].call(this, a0);
//    }
//  });


function Where(stack){
  var at = ""
  for(var i = 0; i < stack.length; ++i){
    at += stack[i].toString() + "\n"
  }
  return at
}

function arrayRemove(arr, value)
{
  return arr.filter(function(ele)
    {
      return ele != value;
    });
}



Java.perform(function()
  {

    var files = [];
    var filenames = [];
    var to_add = false;

    Interceptor.attach(Module.findExportByName("libc.so" , "open"), {
      onEnter: function(args) {
        var path = Memory.readCString(ptr(args[0]));
        if ( !path.startsWith("/dev") &&
          !path.startsWith("/sys") &&
          !path.endsWith(".lock"))
        {
          to_add = true;
          //send("open("+ path + "," + args[1] + ")");
          filenames.push(path);
        }
        //if ( path.startsWith("/data/misc/keychain/pins"))
        //{
        //  var threadef = Java.use('java.lang.Thread')
        //  var threadinstance = threadef.$new()
        //  var stack = threadinstance.currentThread().getStackTrace();
        //  send(Where(stack));
        //}
      },
      onLeave:function(retval){
        if (to_add)
        {
          files.push(retval.toInt32());
          //send("file open "+ filenames.slice(-1)[0] + " : " + retval.toInt32())
          to_add = false;
        }
      }
    });

    Interceptor.attach(Module.findExportByName("libc.so", "close"),
      {
        onEnter: function(args)
        {
          if (files.indexOf(args[0].toInt32()) != -1)
          {
            var filename = filenames[files.indexOf(args[0].toInt32())];
            files = arrayRemove(files, args[0].toInt32());
            filenames = arrayRemove(filenames, filename);
            //send("file -- [" + filename + "] close");
            send(filename);
          }
        },
        onLeave: function(retval)
        {
        }
      });

    //Interceptor.attach(Module.findExportByName("libc.so", "close"),
    //  {
    //    onEnter: function(args)
    //    {
    //      if (files.indexOf(args[0]) != -1)
    //        send("Buffer: ");// + hexdump(Memory.readByteArray(args[1], args[2])));
    //    },
    //    onLeave: function(retval)
    //    {
    //    }
    //  });



  });
