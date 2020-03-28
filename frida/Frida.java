import java.io.IOException;

public class Frida {
    public static void main(String[] args) {
        try
        {
          Process process = Runtime.getRuntime().exec("/data/local/tmp/frida-server");
          System.out.println("Frida load");
        } catch (IOException e) {
          e.printStackTrace();
        }
    }
}

