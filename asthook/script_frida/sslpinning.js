function android_pinning(){
  setTimeout(function() {
    // OkHTTPv3 (double bypass)
    try {
      var okhttp3_Activity = Java.use('okhttp3.CertificatePinner');
      okhttp3_Activity.check.overload('java.lang.String', 'java.util.List').implementation = function (str) {
        console.log('[+] Bypassing OkHTTPv3 {1}: ' + str);
        return true;
      };
      // This method of CertificatePinner.check could be found in some old Android app
      okhttp3_Activity.check.overload('java.lang.String', 'java.security.cert.Certificate').implementation = function (str) {
        console.log('[+] Bypassing OkHTTPv3 {2}: ' + str);
        return true;
      };

    } catch (err) {
      console.log('[-] OkHTTPv3 pinner not found');
      //console.log(err);
    }



    // Trustkit (triple bypass)
    try {
      var trustkit_Activity = Java.use('com.datatheorem.android.trustkit.pinning.OkHostnameVerifier');
      trustkit_Activity.verify.overload('java.lang.String', 'javax.net.ssl.SSLSession').implementation = function (str) {
        console.log('[+] Bypassing Trustkit {1}: ' + str);
        return true;
      };
      trustkit_Activity.verify.overload('java.lang.String', 'java.security.cert.X509Certificate').implementation = function (str) {
        console.log('[+] Bypassing Trustkit {2}: ' + str);
        return true;
      };
      var trustkit_PinningTrustManager = Java.use('com.datatheorem.android.trustkit.pinning.PinningTrustManager');
      trustkit_PinningTrustManager.checkServerTrusted.implementation = function () {
        console.log('[+] Bypassing Trustkit {3}');
      };

    } catch (err) {
      console.log('[-] Trustkit pinner not found');
      //console.log(err);
    }

    // TrustManagerImpl (Android > 7)
    try {
      var OpenSSLSocketImpl = Java.use('com.android.org.conscrypt.OpenSSLSocketImpl');
      OpenSSLSocketImpl.verifyCertificateChain.implementation = function (certRefs, JavaObject, authMethod) {
        console.log('[+] Bypassing OpenSSLSocketImpl Conscrypt');
      };

    } catch (err) {
      console.log('[-] OpenSSLSocketImpl Conscrypt pinner not found');
    }
    // Appcelerator Titanium
    try {
      var appcelerator_PinningTrustManager = Java.use('appcelerator.https.PinningTrustManager');
      appcelerator_PinningTrustManager.checkServerTrusted.implementation = function () {
        console.log('[+] Bypassing Appcelerator PinningTrustManager');
      };

    } catch (err) {
      console.log('[-] Appcelerator PinningTrustManager pinner not found');
      //console.log(err);
    }



    // OpenSSLSocketImpl Conscrypt
    //try {
    //  var OpenSSLSocketImpl = Java.use('com.android.org.conscrypt.OpenSSLSocketImpl');
    //  OpenSSLSocketImpl.verifyCertificateChain.implementation = function (certRefs, JavaObject, authMethod) {
    //    console.log('[+] Bypassing OpenSSLSocketImpl Conscrypt');
    //  };

    //} catch (err) {
    //  console.log('[-] OpenSSLSocketImpl Conscrypt pinner not found');
    //  //console.log(err);        
    //}


    // OpenSSLEngineSocketImpl Conscrypt
    try {
      var OpenSSLEngineSocketImpl_Activity = Java.use('com.android.org.conscrypt.OpenSSLEngineSocketImpl');
      OpenSSLSocketImpl_Activity.verifyCertificateChain.overload('[Ljava.lang.Long;', 'java.lang.String').implementation = function (str1, str2) {
        console.log('[+] Bypassing OpenSSLEngineSocketImpl Conscrypt: ' + str2);
      };

    } catch (err) {
      console.log('[-] OpenSSLEngineSocketImpl Conscrypt pinner not found');
      //console.log(err);
    }



    // OpenSSLSocketImpl Apache Harmony
    try {
      var OpenSSLSocketImpl_Harmony = Java.use('org.apache.harmony.xnet.provider.jsse.OpenSSLSocketImpl');
      OpenSSLSocketImpl_Harmony.verifyCertificateChain.implementation = function (asn1DerEncodedCertificateChain, authMethod) {
        console.log('[+] Bypassing OpenSSLSocketImpl Apache Harmony');
      };

    } catch (err) {
      console.log('[-] OpenSSLSocketImpl Apache Harmony pinner not found');
      //console.log(err);      
    }

    // PhoneGap sslCertificateChecker (https://github.com/EddyVerbruggen/SSLCertificateChecker-PhoneGap-Plugin)
    try {
      var phonegap_Activity = Java.use('nl.xservices.plugins.sslCertificateChecker');
      phonegap_Activity.execute.overload('java.lang.String', 'org.json.JSONArray', 'org.apache.cordova.CallbackContext').implementation = function (str) {
        console.log('[+] Bypassing PhoneGap sslCertificateChecker: ' + str);
        return true;
      };

    } catch (err) {
      console.log('[-] PhoneGap sslCertificateChecker pinner not found');
      //console.log(err);
    }



    // IBM MobileFirst pinTrustedCertificatePublicKey (double bypass)
    try {
      var WLClient_Activity = Java.use('com.worklight.wlclient.api.WLClient');
      WLClient_Activity.getInstance().pinTrustedCertificatePublicKey.overload('java.lang.String').implementation = function (cert) {
        console.log('[+] Bypassing IBM MobileFirst pinTrustedCertificatePublicKey {1}: ' + cert);
        return;
      };
      WLClient_Activity.getInstance().pinTrustedCertificatePublicKey.overload('[Ljava.lang.String;').implementation = function (cert) {
        console.log('[+] Bypassing IBM MobileFirst pinTrustedCertificatePublicKey {2}: ' + cert);
        return;
      };

    } catch (err) {
      console.log('[-] IBM MobileFirst pinTrustedCertificatePublicKey pinner not found');
      //console.log(err);
    }



    // IBM WorkLight (ancestor of MobileFirst) HostNameVerifierWithCertificatePinning (quadruple bypass)
    try {
      var worklight_Activity = Java.use('com.worklight.wlclient.certificatepinning.HostNameVerifierWithCertificatePinning');
      worklight_Activity.verify.overload('java.lang.String', 'javax.net.ssl.SSLSocket').implementation = function (str) {
        console.log('[+] Bypassing IBM WorkLight HostNameVerifierWithCertificatePinning {1}: ' + str);
        return;
      };
      worklight_Activity.verify.overload('java.lang.String', 'java.security.cert.X509Certificate').implementation = function (str) {
        console.log('[+] Bypassing IBM WorkLight HostNameVerifierWithCertificatePinning {2}: ' + str);
        return;
      };
      worklight_Activity.verify.overload('java.lang.String', '[Ljava.lang.String;', '[Ljava.lang.String;').implementation = function (str) {
        console.log('[+] Bypassing IBM WorkLight HostNameVerifierWithCertificatePinning {3}: ' + str);
        return;
      };
      worklight_Activity.verify.overload('java.lang.String', 'javax.net.ssl.SSLSession').implementation = function (str) {
        console.log('[+] Bypassing IBM WorkLight HostNameVerifierWithCertificatePinning {4}: ' + str);
        return true;
      };

    } catch (err) {
      console.log('[-] IBM WorkLight HostNameVerifierWithCertificatePinning pinner not found');
      //console.log(err);
    }

    // Conscrypt CertPinManager
    try {
      var conscrypt_CertPinManager_Activity = Java.use('com.android.org.conscrypt.CertPinManager');
      conscrypt_CertPinManager_Activity.isChainValid.overload('java.lang.String', 'java.util.List').implementation = function (str) {
        console.log('[+] Bypassing Conscrypt CertPinManager: ' + str);
        return true;
      };

    } catch (err) {
      console.log('[-] Conscrypt CertPinManager pinner not found');
      //console.log(err);
    }



    // CWAC-Netsecurity (unofficial back-port pinner for Android < 4.2) CertPinManager
    try {
      var cwac_CertPinManager_Activity = Java.use('com.commonsware.cwac.netsecurity.conscrypt.CertPinManager');
      cwac_CertPinManager_Activity.isChainValid.overload('java.lang.String', 'java.util.List').implementation = function (str) {
        console.log('[+] Bypassing CWAC-Netsecurity CertPinManager: ' + str);
        return true;
      };

    } catch (err) {
      console.log('[-] CWAC-Netsecurity CertPinManager pinner not found');
      //console.log(err);
    }



    // Worklight Androidgap WLCertificatePinningPlugin
    try {
      var androidgap_WLCertificatePinningPlugin_Activity = Java.use('com.worklight.androidgap.plugin.WLCertificatePinningPlugin');
      androidgap_WLCertificatePinningPlugin_Activity.execute.overload('java.lang.String', 'org.json.JSONArray', 'org.apache.cordova.CallbackContext').implementation = function (str) {
        console.log('[+] Bypassing Worklight Androidgap WLCertificatePinningPlugin: ' + str);
        return true;
      };

    } catch (err) {
      console.log('[-] Worklight Androidgap WLCertificatePinningPlugin pinner not found');
      //console.log(err);
    }



    // Netty FingerprintTrustManagerFactory
    try {
      var netty_FingerprintTrustManagerFactory = Java.use('io.netty.handler.ssl.util.FingerprintTrustManagerFactory');
      //NOTE: sometimes this below implementation could be useful
      //var netty_FingerprintTrustManagerFactory = Java.use('org.jboss.netty.handler.ssl.util.FingerprintTrustManagerFactory');
      netty_FingerprintTrustManagerFactory.checkTrusted.implementation = function (type, chain) {
        console.log('[+] Bypassing Netty FingerprintTrustManagerFactory');
      };

    } catch (err) {
      console.log('[-] Netty FingerprintTrustManagerFactory pinner not found');
      //console.log(err);
    }

    // Squareup CertificatePinner [OkHTTP < v3] (double bypass)
    try {
      var Squareup_CertificatePinner_Activity = Java.use('com.squareup.okhttp.CertificatePinner');
      Squareup_CertificatePinner_Activity.check.overload('java.lang.String', 'java.security.cert.Certificate').implementation = function (str1, str2) {
        console.log('[+] Bypassing Squareup CertificatePinner {1}: ' + str1);
        return;
      };

      Squareup_CertificatePinner_Activity.check.overload('java.lang.String', 'java.util.List').implementation = function (str1, str2) {
        console.log('[+] Bypassing Squareup CertificatePinner {2}: ' + str1);
        return;
      };

    } catch (err) {
      console.log('[-] Squareup CertificatePinner pinner not found');
      //console.log(err);
    }



    // Squareup OkHostnameVerifier [OkHTTP v3] (double bypass)
    try {
      var Squareup_OkHostnameVerifier_Activity = Java.use('com.squareup.okhttp.internal.tls.OkHostnameVerifier');
      Squareup_OkHostnameVerifier_Activity.verify.overload('java.lang.String', 'java.security.cert.X509Certificate').implementation = function (str1, str2) {
        console.log('[+] Bypassing Squareup OkHostnameVerifier {1}: ' + str1);
        return true;
      };

      Squareup_OkHostnameVerifier_Activity.verify.overload('java.lang.String', 'javax.net.ssl.SSLSession').implementation = function (str1, str2) {
        console.log('[+] Bypassing Squareup OkHostnameVerifier {2}: ' + str1);
        return true;
      };

    } catch (err) {
      console.log('[-] Squareup OkHostnameVerifier pinner not found');
      //console.log(err);
    }



    // Android WebViewClient
    try {
      var AndroidWebViewClient_Activity = Java.use('android.webkit.WebViewClient');
      AndroidWebViewClient_Activity.onReceivedSslError.overload('android.webkit.WebView', 'android.webkit.SslErrorHandler', 'android.net.http.SslError').implementation = function (obj1, obj2, obj3) {
        console.log('[+] Bypassing Android WebViewClient');
      };

    } catch (err) {
      console.log('[-] Android WebViewClient pinner not found');
      //console.log(err);
    }
    // Apache Cordova WebViewClient
    try {
      var CordovaWebViewClient_Activity = Java.use('org.apache.cordova.CordovaWebViewClient');
      CordovaWebViewClient_Activity.onReceivedSslError.overload('android.webkit.WebView', 'android.webkit.SslErrorHandler', 'android.net.http.SslError').implementation = function (obj1, obj2, obj3) {
        console.log('[+] Bypassing Apache Cordova WebViewClient');
        obj3.proceed();
      };

    } catch (err) {
      console.log('[-] Apache Cordova WebViewClient pinner not found');
      //console.log(err):
    }



    // Boye AbstractVerifier
    try {
      var boye_AbstractVerifier = Java.use('ch.boye.httpclientandroidlib.conn.ssl.AbstractVerifier');
      boye_AbstractVerifier.verify.implementation = function (host, ssl) {
        console.log('[+] Bypassing Boye AbstractVerifier: ' + host);
      };

    } catch (err) {
      console.log('[-] Boye AbstractVerifier pinner not found');
      //console.log(err):
    }


    //try {

    //} catch (err) {
    //  console.log('[-] Conscrypt CertPinManager pinner not found');
    //console.log(err);
    //}



  }, 0);

}

send("Universal SSl pinning enable")
Java.perform(function()
  {

    var class_not_found = Java.use('java.lang.ClassNotFoundException')

    // Seems to have a bave a backdoor on /data/misc/keychain/pins (put your
    // certificate here and everythings will be bypass
    // Conscrypt
    try
    {
      var conscrypt_CertPinManager_Activity = Java.use('com.android.org.conscrypt.CertPinManager');
      conscrypt_CertPinManager_Activity.isChainValid.overload('java.lang.String', 'java.util.List').implementation = function (str, chain) {
        send('Bypassing Conscrypt CertPinManager: ' + str);
        return true;
      };
      send('Found: Conscrypt CertPinManager');
    }
    catch (e)
    {
      //if (!( instanceof class_not_found))
      //send(e);
    }


    // oKHTTPv3
    try
    {
      var okhttp3_Activity = Java.use('okhttp3.CertificatePinner');
      okhttp3_Activity.check.overload('java.lang.String', 'java.util.List').implementation = function (str) {
        console.log('[+] Bypassing OkHTTPv3 {1}: ' + str);
        return true;
      };
      send('Found: OkHTTPv3');
    }
    catch (e)
    {
      //if ( ! (instanceof class_not_found))
      //send(e);
    }
    
    
    try
    {
      var OpenSSLSocketImpl = Java.use('com.android.org.conscrypt.OpenSSLSocketImpl');
      OpenSSLSocketImpl.verifyCertificateChain.implementation = function (certRefs, JavaObject, authMethod) {
        send('Bypassing OpenSSLSocketImpl Conscrypt: ');
      };
      send('Found: OpenSSLSocketImpl Conscrypt');
    }
    catch (e)
    {
      //if ( ! (instanceof class_not_found))
      //send(e);
    }

    try
    {
      var array_list = Java.use("java.util.ArrayList");
      var ApiClient = Java.use('com.android.org.conscrypt.TrustManagerImpl');

      ApiClient.checkTrustedRecursive.implementation = function(a1,a2,a3,a4,a5,a6) {
        // console.log('Bypassing SSL Pinning');
        send('Bypassing TrustManager to enable all SSLpining');
        var k = array_list.$new();
        return k;
      }
      send('Found: TrustManager');
    }
    catch (e) {}

    try
    {
      var TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');
      var ArrayList = Java.use("java.util.ArrayList");
      TrustManagerImpl.verifyChain.implementation = function(untrustedChain, trustAnchorChain,
        host, clientAuth, ocspData, tlsSctData) {
        send("Bypassing TrustManagerImpl->verifyChain()");
        return untrustedChain;
      };
      TrustManagerImpl.checkTrustedRecursive.implementation = function(certs, host, clientAuth, untrustedChain, trustAnchorChain, used) {
        send("Bypassing TrustManagerImpl->checkTrustedRecursive()");
        return ArrayList.$new();
      };
      send("Found: TrustMangerImpl conscrypt");
    }
    catch (e) {}


    /*    try
    {
      //var TrustManagerImpl = Java.use("com.android.org.conscrypt.TrustManagerImpl")
      var Platform = Java.use("com.android.org.conscrypt.Platform");
//var TrustManagerImpl = Java.use("TrustManagerImpl$ExtendedKeyUsagePKIXCertPathChecker")
      var ArrayList = Java.use("java.util.ArrayList");

//send(Object.getOwnPropertyNames(TrustManagerImpl.__proto__).join('\n\t'));
//var a = TrustManagerImpl.class.getDeclaredMethods();
//TrustManagerImpl.$dispose;
//a.forEach(function(s) {
//  send(s.toString());
//});
//send('Found: com.android.org.conscrypt.TrustManagerImpl');
      Platform.checkServerTrusted.overload('javax.net.ssl.X509TrustManager', '[Ljava.security.cert.X509Certificate;', 'java.lang.String', 'com.android.org.conscrypt.AbstractConscryptSocket').implementation = function(a, b, c, d){
  //TrustManagerImpl.verifyChain.implementation = function(a, b, c, d) {
  //TrustManagerImpl.checkTrustedRecursive.implementation = function() {
  //TrustManagerImpl.checkServerTrusted.implementation = function() {
        send("[+] Bypassing TrustManagerImpl->verifyChain()");
//  return a;
      }
//TrustManagerImpl.checkTrustedRecursive.implementation = function(certs, host, clientAuth, untrustedChain,
//  trustAnchorChain, used) {
//  send("[+] Bypassing TrustManagerImpl->checkTrustedRecursive()");
//  return ArrayList.$new();
//};
      Platform.checkServerTrusted.overload('javax.net.ssl.X509TrustManager', '[Ljava.security.cert.X509Certificate;', 'java.lang.String', 'com.android.org.conscrypt.ConscryptEngine').implementation = function(a, b, c, d){
        send("[+] Bypassing TrustManagerImpl->verifyChain()");
      }
      send('Found: com.android.org.conscrypt.TrustManagerImpl');
    }
    catch (e) {send(e.toString())}
    */

});
//android_pinning()
//Java.perform(function() {
//    Java.enumerateLoadedClasses({
//        onMatch: function(className) {
//            console.log(className);
//        },
//        onComplete: function() {}
//    });
//});
