import org.arl.fjage.*
import org.arl.fjage.remote.*
import org.arl.fjage.shell.*

def webshPort = 8081
def jsonPort = 1100

boolean gui = System.properties.getProperty('fjage.gui') == 'true'
int port = 5081
try {
  port =  Integer.parseInt(System.properties.getProperty('fjage.port'))
} catch (Exception ex) {
  // do nothing
}
String devname = System.properties.getProperty('fjage.devname')
int baud = 9600
if (devname != null) {
  try {
    baud =  Integer.parseInt(System.properties.getProperty('fjage.baud'))
  } catch (Exception ex) {
    // do nothing
  }
}

platform = new RealTimePlatform()
if (devname == null) container = new MasterContainer(platform, port)
else container = new MasterContainer(platform, port, devname, baud, 'N81')
if (gui) shell = new ShellAgent(new SwingShell(), new GroovyScriptEngine())
else shell = new ShellAgent(new ConsoleShell(), new GroovyScriptEngine())
container.add 'shell', shell
def ws = new WebShell(webshPort, '/')
ws.htmlBody =  ws.html
webshell = new ShellAgent(ws, new GroovyScriptEngine(true))
container.add 'websh', webshell
webshell.addInitrc 'etc/fshrc.groovy'
webshell.addInitrc 'cls://org.arl.yoda.shell.fshrc'
container.openWebSocket(ws.contextHandler)
platform.start()
