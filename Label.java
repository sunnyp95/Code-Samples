package coffeecard.fluttertools.puqu_label_printer;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

//Label class to handle formatting
//Units are milimeters(mm)
//All hard-coded addition and subtractions are spacing in mm
//hard-coded division and multiple are for scaling relative to label size

public class Label {
    private String customerName;
    private List<String> order;
    private String time;
    private String vendorLogoPath;
    private String companyLogoPath;
    private String QRurl;
    private double height;
    private double width;
    private double yPosition = 1.0; //1mm from upper left

    public void setCustomerName(String customerName) {
        this.customerName = customerName;
    }

    public void setOrder(List<String> order) {
        this.order = order;
    }

    public void setTime(String time) {
        this.time = time;
    }

    public void setVendorLogoPath(String vendorLogoPath) {
        this.vendorLogoPath = vendorLogoPath;
    }

    public void setCompanyLogoPath(String companyLogoPath) {
        this.companyLogoPath = companyLogoPath;
    }

    public void setQRurl(String QRurl) {
        this.QRurl = QRurl;
    }

    public void setHeight(double height) {
        this.height = height;
    }

    public void setWidth(double width) {
        this.width = width;
    }

    public void setYPosition(double yPosition){
        this.yPosition = yPosition;
    }

    public void resetYPosition(){
        this.yPosition = 0.0;
    }

    public String getCustomerName() {
        return customerName;
    }

    public List<String> getOrder() {
        return order;
    }

    public String getTime() {
        return time;
    }

    public String getVendorLogoPath() {
        return vendorLogoPath;
    }

    public String getCompanyLogoPath() {
        return companyLogoPath;
    }

    public String getQRurl() {
        return QRurl;
    }

    public double getHeight() {
        return height;
    }

    public double getWidth() {
        return width;
    }



    public Map<String, Double> getTimeParams(){
        Map<String, Double> params = new HashMap<String, Double>();
        Double fontHeight = .02*getHeight()+1.9;
        Double xPosition = getWidth()-2;
        params.put("xPosition", xPosition);
        params.put("yPosition", this.yPosition);
        params.put("fontHeight", fontHeight);
        return params;
    }

    public Map<String, Double> getLogoParams(){
        Map<String, Double> params = new HashMap<String, Double>();
        this.yPosition += 1 + getHeight()/12;
        Double imageWidth = getWidth()/3;
        Double imageHeight = imageWidth;
        Double xPosition = getWidth()/2;
        Double fontHeight = imageWidth/4;
        params.put("xPosition", xPosition);
        params.put("yPosition", this.yPosition);
        params.put("imageWidth", imageWidth);
        params.put("imageHeight", imageHeight);
        params.put("fontHeight", fontHeight);
        return params;
    }

    public Map<String, Double> getNameParams(){
        Map<String, Double> params = new HashMap<String, Double>();
        this.yPosition += getWidth()/3 + 3;
        Double xPosition = getWidth()/2;
        Double fontHeight = getHeight()/12;
        params.put("xPosition", xPosition);
        params.put("yPosition", this.yPosition);
        params.put("fontHeight", fontHeight);
        return params;
    }

    public Map<String, Double> getOrderParams(){
        Map<String, Double> params = new HashMap<String, Double>();
        this.yPosition += getHeight()/12 + 1;
        Double xPosition = getWidth()/2;
        Double fontHeight = getHeight()/18;
        params.put("xPosition", xPosition);
        params.put("yPosition", this.yPosition);
        params.put("fontHeight", fontHeight);
        return params;
    }

    public Map<String, Double> getQRParams(){
        Map<String, Double> params = new HashMap<String, Double>();
        Double imageWidth = getWidth()/3;
        Double xPosition = getWidth()/2 - imageWidth/2;
        this.yPosition = getHeight()-imageWidth-2;
        params.put("xPosition", xPosition);
        params.put("yPosition", this.yPosition);
        params.put("imageWidth", imageWidth);
        return params;
    }
}