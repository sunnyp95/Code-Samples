package coffeecard.fluttertools.puqu_label_printer;

import androidx.annotation.NonNull;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

import io.flutter.embedding.engine.plugins.FlutterPlugin;
import io.flutter.plugin.common.MethodCall;
import io.flutter.plugin.common.MethodChannel;
import io.flutter.plugin.common.MethodChannel.MethodCallHandler;
import io.flutter.plugin.common.MethodChannel.Result;
import io.flutter.plugin.common.PluginRegistry.Registrar;

import com.dothantech.lpapi.LPAPI;
import com.dothantech.lpapi.LPAPI.Factory;
import com.dothantech.printer.IDzPrinter.PrinterState;


/** PuquLabelPrinterPlugin */
public class PuquLabelPrinterPlugin implements FlutterPlugin, MethodCallHandler {
  /// The MethodChannel that will the communication between Flutter and native Android
  ///
  /// This local reference serves to register the plugin with the Flutter Engine and unregister it
  /// when the Flutter Engine is detached from the Activity
  private MethodChannel channel;
  private LPAPI api = Factory.createInstance();  //printer api that will handle all printer related calls
  private String printerName; //current printer connected
  private Label label = new Label(); //label object to handle formatting

  //initializes channel
  @Override
  public void onAttachedToEngine(@NonNull FlutterPluginBinding flutterPluginBinding) {
    channel = new MethodChannel(flutterPluginBinding.getBinaryMessenger(), "puqu_label_printer");
    channel.setMethodCallHandler(this);
  }

  //breaks channel
  @Override
  public void onDetachedFromEngine(@NonNull FlutterPluginBinding binding) {
    channel.setMethodCallHandler(null);
  }


  //routes all platforms methods from flutter
  @Override
  public void onMethodCall(@NonNull MethodCall call, @NonNull Result result) {
    switch(call.method){
      case "connectPrinter":
        final String name = call.argument("printerName");
        try{
          result.success(connectPrinter(name));
        }
        catch (Exception e){
          result.error("Printer Connection Error", e.getMessage(), e.getStackTrace());
        }
        break;
      case "disconnectPrinter":
        try {
          result.success(disconnectPrinter());
        }
        catch (Exception e){
          result.error("Printer Disconnection Error", e.getMessage(), e.getStackTrace());
        }
        break;
      case "createLabel":
        try {
          final String customerName = call.argument("customerName");
          final List<String> order = call.argument("order");
          final String time = call.argument("time");
          final String vendor = call.argument("vendorLogoPath");
          final String company = call.argument("companyLogoPath");
          final String qr = call.argument("QRurl");
          final double height = call.argument("height");
          final double width = call.argument("width");
          result.success(createLabel(customerName, order, time, vendor, company, qr, height, width));
        }catch (Exception e){
          result.error("Label Creation Error", e.getMessage(), Arrays.toString(e.getStackTrace()));
        }
        break;
      case "printLabel":
        try {
          result.success(printLabel());
        }catch (Exception e) {
          result.error("Print Error", e.getMessage(), Arrays.toString(e.getStackTrace()));
        }
        break;
      default:
        result.notImplemented();
    }
  }

  //true if successful else false
  private boolean connectPrinter(String name){
    PrinterState state = api.getPrinterState();
    // Printer is not connected
    if (state == null || state.equals(PrinterState.Disconnected)) {
      return false;
    }
    this.printerName = name;
    return true;
  }

  //true if successful else false
  private boolean disconnectPrinter(){
    PrinterState state = api.getPrinterState();
    // Printer is not connected
    if (state == null || state.equals(PrinterState.Disconnected)) {
      this.printerName = null;
      return true;
    }
    return false;
  }

  //true if successful else false
  private boolean createLabel(String customerName, List<String> order, String time,
                           String vendorLogoPath, String companyLogoPath, String QRurl, double height, double width){
    try {
      label.setCustomerName(customerName);
      label.setOrder(order);
      label.setTime(time);
      label.setVendorLogoPath(vendorLogoPath);
      label.setCompanyLogoPath(companyLogoPath);
      label.setQRurl(QRurl);
      label.setHeight(height);
      label.setWidth(width);
      label.resetYPosition();
      return true;
    } catch (Exception e){
      return false;
    }
  }

  //true if successful else false
  private boolean printLabel(){
    api.openPrinter(printerName); //open printer for printing
    api.startJob(label.getWidth(), label.getHeight(), 0); //start job by specifying label dimensions
    api.setItemHorizontalAlignment(2); // right align
    drawTime(); //time is drawn
    api.setItemHorizontalAlignment(1); //center align
    drawLogos(); //logos are drawn
    drawName(); //name is drawn
    drawOrder(); //order is drawn
    api.setItemVerticalAlignment(2); //bottom align
    drawQR(); //qr is generated
    return(api.commitJob()); //buffer is submitted to printer for printing
  }

  //gets format params of time and draws it
  private void drawTime(){
    Map<String, Double> params = label.getTimeParams();
    api.drawText(label.getTime(), params.get("xPosition"), params.get("yPosition"), 0, 0, params.get("fontHeight"));
  }

  //gets format params of logos and draws it
  private void drawLogos(){
    Map<String, Double> params = label.getLogoParams();
    api.drawImage(label.getCompanyLogoPath(), params.get("xPosition")-params.get("imageWidth")-2, params.get("yPosition"), params.get("imageWidth"), params.get("imageHeight"));
    api.drawText("X", params.get("xPosition"), params.get("yPosition")+(params.get("imageHeight")/3), 0, 0, params.get("fontHeight"));
    api.drawImage(label.getVendorLogoPath(), params.get("xPosition")+2, params.get("yPosition"), params.get("imageWidth"), params.get("imageHeight"));
  }

  //gets format params of name and draws it
  private void drawName(){
    Map<String, Double> params = label.getNameParams();
    api.drawText(label.getCustomerName(), params.get("xPosition"), params.get("yPosition"), 0, 0, params.get("fontHeight"));
  }

  //gets format params of order and draws it
  private void drawOrder(){
    Map<String, Double> params = label.getOrderParams();
    double yPosition = params.get("yPosition");
    List<String> order = label.getOrder();
    for(int i=0; i<order.size(); i++){ //loops through each instruction and prints each on a line
      String orderItem = order.get(i);
      api.drawText(orderItem, params.get("xPosition"), yPosition, 0, 0, params.get("fontHeight"));
      yPosition += params.get("fontHeight");
    }
    label.setYPosition(yPosition);
  }

  //gets format params of qr code, generates, and draws it
  private void drawQR(){
    Map<String, Double> params = label.getQRParams();
    api.draw2DQRCode(label.getQRurl(), params.get("xPosition"), params.get("yPosition"), params.get("imageWidth"));
  }

}
