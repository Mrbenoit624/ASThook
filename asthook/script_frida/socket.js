
Java.perform(function()
  {

    function Where(stack){
      var at = ""
      for(var i = 0; i < stack.length; ++i){
        at += stack[i].toString() + "\n"
      }
      return at
    }

    //Interceptor.attach(Module.findExportByName("libc.so" , "send"), {
    //  onEnter: function(args) {
    //    send("a socket send is called");
    //    var threadef = Java.use('java.lang.Thread')
    //    var threadinstance = threadef.$new()
    //    var stack = threadinstance.currentThread().getStackTrace();
    //    send(Where(stack));
    //  },
    //  onLeave:function(retval){
    //  }
    //});
    
    var sockets = [];
    var to_add = false;

    Interceptor.attach(Module.findExportByName("libc.so" , "socket"), {
      onEnter: function(args) {
        var type = args[0].toInt32();
        if (type == 10 || type == 3 || type == 4)
        {
          //send("type: " + type);
          to_add = true;
        }
      },
      onLeave:function(retval){
        if (to_add)
        {
          sockets.push(retval.toInt32());
          //send("ret: " + retval.toInt32());
          to_add = false;
        }
      }
    });
    
    
    //Interceptor.attach(Module.findExportByName("libc.so" , "send"), {
    //  onEnter: function(args) {
    //    if (sockets.indexOf(args[0].toInt32()) != -1)
    //      send(Memory.readCString(args[1]));
    //  },
    //  onLeave:function(retval){
    //  }
    //});
    
    
    // TODO: Manque d'un mouvement latérale pour accéder à la fonction qui
    // permet le ssl pinning
    Interceptor.attach(Module.findExportByName("libc.so" , "write"), {
      onEnter: function(args) {
        if (sockets.indexOf(args[0].toInt32()) != -1)
        {
          //send("write : " + Memory.readCString(args[1]));
          var threadef = Java.use('java.lang.Thread')
          var threadinstance = threadef.$new()
          var stack = threadinstance.currentThread().getStackTrace();
          send(Where(stack))
        }
      },
      onLeave:function(retval){
      }
    });

    //var CloseGuard = Java.use('dalvik.system.CloseGuard')
    //Interceptor.attach(CloseGuard, 
    //  {
    //    onEnter: function(args)
    //    {
    //      var threadef = Java.use('java.lang.Thread')
    //      var threadinstance = threadef.$new()
    //      var stack = threadinstance.currentThread().getStackTrace();
    //      send(Where(stack));
    //    },
    //    onLeave:function(retval)
    //    {
    //    }
    //  });



  });
