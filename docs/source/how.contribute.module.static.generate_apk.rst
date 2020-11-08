Generate APK
============

To generate an apk you should generate JavaFile with the format Jinja2 and then
call the function GenerateAPK with:
- the name of the apk to build
- the JavaFile for the manifest
- the list of JavaFile of the APK
- args to build the apk
- tmp_dir the path where the apk is store

.. code-block:: python

  from asthook.static.generate_apk import GenerateAPK, JavaFile

  manifest = JavaFile("/AndroidManifest.xml",
           path + "AndroidManifest.xml",
           {'app' : app,
            'activity' : activity})
   exploit = JavaFile("/exploit/intent/exploit.java",
           path + "/java/exploit/intent/exploit.java",
           {'app' : app,
            'activity' : activity,
            'parameters' : parameters,
            'data': Data,
            'datas': Datas})
   GenerateAPK("vulnIntent_%s_%s" % (activity, k),
           manifest,
           [exploit],
           self.args, self.get_tmp())
