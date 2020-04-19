Java.perform(function() {
  var f = Java.use("java.io.File");
  f.delete.implementation = function(a){
    var s = this.getAbsolutePath();
    //if(s.includes("dex")){
      send(this.getAbsolutePath());
      var get_file = recv('input', function(value) {});
      get_file.wait();
      var ret = this.delete();
      console.log("[+] Delete catched =>" +this.getAbsolutePath());
    //}
    return ret;
  }
});
