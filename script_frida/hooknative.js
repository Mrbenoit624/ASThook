
function trace(pattern)
{
  var str = "exports:*!";
  str = str.concat(pattern);
  var res = new ApiResolver('module');
  var matches = res.enumerateMatchesSync(str);
  //var targets = uniqBy(matches, JSON.stringify);
  matches.forEach(function(target) {
    traceModule(target.address, target.name);
  });
}

function traceModule(impl, name)
{
  console.log("Tracing " + name);
  Interceptor.attach(impl, {
    onEnter: function(args) {
      for (var i = 0; i < arguments.length; i++)
      {
        //console.log("arg" + i + " : " + Memory.readCString(args[i]));
        send("arg" + i + " : " + args[i]);
        send("arg" + i + " : " + Memory.readCString(args[i]));
      }
      send("*** entered " + name);
      // print backtrace
      //send("Backtrace:\n" + Thread.backtrace(this.context, Backtracer.ACCURATE)
      //  .map(DebugSymbol.fromAddress).join("\n"));
    },
    onLeave: function(retval) {
      if (this.flag) {
        // print retval
        send("retval: " + retval);
        send("*** exiting " + name);
      }
    }
  });
}

//Java.perform(function() {
//  trace("open*");
//});
