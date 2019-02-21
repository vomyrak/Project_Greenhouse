//
//  ViewController.swift
//  hangge_2287
//
//  Created by hangge on 2019/1/25.
//  Copyright © 2019 hangge. All rights reserved.
//

import UIKit
import WebKit
import AAInfographics
import CocoaMQTT


class ViewController: UIViewController {
    
    struct Measurements: Decodable{
        var temperature: Float
        var organic: Int
        var humidity: Float
        var co2: Int
        var time: String
    }
    //define a struct include temperature, organic, humidity, co2 and time


    
    var mqtt: CocoaMQTT!
    var i=0
    
    var tempHist = [Float](repeating: 0.0, count: 20)   //measure the temperature every second, every plot we take 20 measurements
    var tempHistDict : [String: Float] = [:]//The historical record of temperature
    var CO2Hist = [Int](repeating: 0, count: 20) //measure the CO2 every second, every plot we take 20 measurements
    var organicHist = [Int](repeating: 0, count: 20) //measure the organic every second, every plot we take 20 measurements
    var humidityHist = [Float](repeating: 0.0, count: 20) //measure the humidity every second, every plot we take 20 measurements
    var humidityHistDict = [String](repeating: "0.0", count: 20) //measure the temperature every second, every plot we take 20 measurements
    
    var chartModel = AAChartModel()
        .chartType(.line)//chart type
        .title("Greenhouse autocontroller")//title of the chart
        .subtitle("Date:")//subtitle
        .animationType(.easeTo)
        .inverted(false)//invert or not
        .yAxisTitle("Temperature/C")// Y axis
        .dataLabelEnabled(false)//do not enable the data label
        .legendEnabled(true)//Enable legend for chart (clickable dots at bottom of chart)
        .tooltipValueSuffix("F")//Floating prompt box with unit suffix
    
    var aaChartView = AAChartView()
    
    @IBOutlet weak var ConnectLabel: UILabel!
    @IBOutlet weak var ConnectLabel2: UILabel!
    @IBOutlet weak var ConnectLabel3: UILabel!
    @IBOutlet weak var ConnectLabel4: UILabel!
    @IBOutlet weak var tempSwitch: UISwitch!
    @IBOutlet weak var co2Switch: UISwitch!
    @IBOutlet weak var organicSwitch: UISwitch!
    @IBOutlet weak var humanitySwitch: UISwitch!
    @IBOutlet weak var historyswitch: UISwitch!
    @IBOutlet var speciesText: UITextField!
    //@IBOutlet weak var button: UIButton!
    
    @IBAction func Tapped(_ sender: Any) {
        //tap in the specie you want to measure
        let str = speciesText.text
        let trimmedstr = str?.trimmingCharacters(in:CharacterSet.whitespaces)//to remove the space in the end of text
        speciesText.text = trimmedstr
        //if type in carnation or parimulas, start to take the measurment. Else, pop out the notification "worry name try again"
        if((trimmedstr != "carnation")&&(trimmedstr != "parimulas")){
            
            let alert = UIAlertController(title: "wrong name", message: "try again ?", preferredStyle: .alert)
            let btnOK = UIAlertAction(title: "Okay", style: .default, handler: nil)
            alert.addAction(btnOK)
            self.present(alert, animated:true,completion: nil)
            historyswitch.setOn(false, animated:true)
        }else{
            let alert = UIAlertController(title: "you select", message: speciesText.text, preferredStyle: .alert)
            let btnOK = UIAlertAction(title: "Okay", style: .default, handler: nil)
            alert.addAction(btnOK)
            self.present(alert, animated:true,completion: nil)
        }
    }
    
    
    @IBAction func History(_ sender: UISwitch) {
       
        if (sender.isOn == true){
            let string = ["flora": speciesText.text]
            let message = try! JSONEncoder().encode(string)
            let json = String(decoding: message, as: UTF8.self)
            mqtt!.publish("Hot_Wings/history_request", withString: json, qos: .qos2)

    //define an UISwitch. When it is on,it publishes a message through mqtt and displays the history reading from remote database; if not, it displays the current reading
            
        }
    }
    
    
    @IBAction func Temperature(_ sender: UISwitch) {
        if (sender.isOn == true){
            // initialise the viewcontroller
            let chartWidth  = self.view.frame.size.width
            let chartHeight = self.view.frame.size.height - 300
             // only temperature graph are shown ,all the others are hidden
            aaChartView.isHidden = false
            co2Switch.isOn = false
            organicSwitch.isOn = false
            humanitySwitch.isOn = false
            //initialise the chart frame
            aaChartView.frame = CGRect(x:0, y:0, width:chartWidth, height:chartHeight)
            // initialise the chart model
            self.view.addSubview(aaChartView)
            var elementArray = [
                AASeriesElement()
                    .name("Temperature/°C")// name of the line
                    .data(tempHist)//data type
                    .toDic()!]
            chartModel.colorsTheme(["#fe117c"])//colour
            //define a x-axis array named categories
            var categories = ["0","1","2","3","4","5","6","7","8","9","10","11","12",
                              "13","14","15","16","17","18","19"]
            
            chartModel.categories = categories;
            chartModel.series = elementArray;
            // Plot the graph
            aaChartView.aa_drawChartWithChartModel(chartModel)
        }
        else if(co2Switch.isOn == false &&
            organicSwitch.isOn == false &&
            humanitySwitch.isOn == false && tempSwitch.isOn == false){
            //when all of the switch button is off, the charts are all hidden
        aaChartView.isHidden = true
        }
    }
    
    @IBAction func CO2(_ sender: UISwitch) {
        if(sender.isOn == true){
            // initialise the viewcontroller
            let chartWidth  = self.view.frame.size.width
            let chartHeight = self.view.frame.size.height - 300
            aaChartView.isHidden = false
            tempSwitch.isOn = false
            organicSwitch.isOn = false
            humanitySwitch.isOn = false
            aaChartView.frame = CGRect(x:0, y:0, width:chartWidth, height:chartHeight)
            // initialise the chart model
            self.view.addSubview(aaChartView)
            var elementArray = [
                AASeriesElement()
                    .name("CO2/ppm")//name of the line
                    .data(CO2Hist)//data type
                    .toDic()!]
            chartModel.colorsTheme(["#ffc069"])//colour
            var categories = ["0","1","2","3","4","5","6","7","8","9","10","11","12",
                              "13","14","15","16","17","18","19"]
            //define a x-axis array named categories
            chartModel.categories = categories;
            chartModel.series = elementArray;
            // Plot the graph
            
            aaChartView.aa_drawChartWithChartModel(chartModel)
        }
        else if(co2Switch.isOn == false &&
            organicSwitch.isOn == false &&
            humanitySwitch.isOn == false && tempSwitch.isOn == false){
            //when all of the switch button is off, the charts are all hidden
            aaChartView.isHidden = true
        }
    }
    
    @IBAction func organic(_ sender: UISwitch) {
        if(sender.isOn == true){
            // initialise the viewcontroller
            let chartWidth  = self.view.frame.size.width
            let chartHeight = self.view.frame.size.height - 300
            aaChartView.isHidden = false
            tempSwitch.isOn = false
            co2Switch.isOn = false
            humanitySwitch.isOn = false
            aaChartView.frame = CGRect(x:0, y:0, width:chartWidth, height:chartHeight)
            // initialise the chart model
            self.view.addSubview(aaChartView)
            var elementArray = [
                AASeriesElement()
                .name("organic/ppb")//name of the line
                .data(organicHist)//data type
                .toDic()!]
            chartModel.colorsTheme(["#06caf4"])//colour
            var categories = ["0","1","2","3","4","5","6","7","8","9","10","11","12",
                              "13","14","15","16","17","18","19"]
            //define a x-axis array called categories
            chartModel.categories = categories;
            chartModel.series = elementArray;
            // Plot the graph
            
            aaChartView.aa_drawChartWithChartModel(chartModel)
        }
        else if(co2Switch.isOn == false &&
            organicSwitch.isOn == false &&
            humanitySwitch.isOn == false && tempSwitch.isOn == false){
            //when all of the switch button is off, the charts are all hidden
            aaChartView.isHidden = true
        }
    }
    
    @IBAction func Humidity(_ sender: UISwitch) {
        if(sender.isOn == true){
            // initialise the viewcontroller
            let chartWidth  = self.view.frame.size.width
            let chartHeight = self.view.frame.size.height - 300
            aaChartView.isHidden = false
            tempSwitch.isOn = false
            organicSwitch.isOn = false
            co2Switch.isOn = false
            aaChartView.frame = CGRect(x:0, y:0, width:chartWidth, height:chartHeight)
            // initialise the chart model
            self.view.addSubview(aaChartView)
            var elementArray = [
                AASeriesElement()
                    .name("humidity/%")//name of the line
                    .data(humidityHist)//datd type
                    .toDic()!]
            chartModel.colorsTheme(["#000000"])//colour
            var categories = ["0","1","2","3","4","5","6","7","8","9","10","11","12",
                              "13","14","15","16","17","18","19"]
            //define a x-axis array called categories
            chartModel.categories = categories;
            chartModel.series = elementArray;
            // Plot the graph
            
            aaChartView.aa_drawChartWithChartModel(chartModel)
        }
        else if(co2Switch.isOn == false &&
            organicSwitch.isOn == false &&
            humanitySwitch.isOn == false && tempSwitch.isOn == false){
            //when all of the switch button is off, the charts are all hidden
            aaChartView.isHidden = true
        }
    }
 
    
    @IBAction func Button2(_ sender: UIButton) {
        // start to ventilate. pop out notification "already ventilated yeah!"
        let control_array = [1, 0, 0, 0] // control message
        let message = try! JSONEncoder().encode(control_array)
        let json = String(decoding: message, as: UTF8.self)
        mqtt!.publish("Hot_Wings/control", withString: json, qos: .qos2)


        let alert = UIAlertController(title: "Relax", message: "already ventilated yeah!", preferredStyle: .alert)
        let btnOK = UIAlertAction(title: "Okay", style: .default, handler: nil)
        alert.addAction(btnOK)
        self.present(alert, animated:true,completion: nil)
    }
    @IBAction func Button(_ sender: UIButton) {
      // start to water. pop out notification "already waterring yeah!"
        let control_array = [0, 0, -1, 0] // control message
        let message = try! JSONEncoder().encode(control_array)
        let json = String(decoding: message, as: UTF8.self)
        mqtt!.publish("Hot_Wings/control", withString: json, qos: .qos2)

        let alert = UIAlertController(title: "Relax", message: "already waterring yeah!", preferredStyle: .alert)
        let btnOK = UIAlertAction(title: "Okay", style: .default, handler: nil)
        alert.addAction(btnOK)
        self.present(alert, animated:true,completion: nil)
    }
    
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        speciesText.delegate = self
        let name = NSNotification.Name(rawValue: "MQTTMessageNotification")
        NotificationCenter.default.addObserver(self, selector:#selector(getdata), name: name, object: nil)

        //selfSignedSSLSetting()  Abandoned due to failure of secure connection
        
        var communicationThread = Thread(target: self, selector: #selector(self.mqttsetting), object: nil)
        communicationThread.start()
    }
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
    
    override func didReceiveMemoryWarning(){
            super.didReceiveMemoryWarning()
        }
    
    //get data from notification center
    @objc func getdata(notification:Notification)-> Void{
        let messageRecieved = notification.userInfo!["message"] as! String;
        let topicRecieved = notification.userInfo!["topic"] as! String;
        
        
        if (topicRecieved == "Hot_Wings/raw_data"){
            //when topic is "raw_data", real time data received
            guard var data = try? JSONDecoder().decode(Measurements.self, from: messageRecieved.data(using: String.Encoding.utf8)!) else {
                print("Invalid data received")
                return
            }
            
            if(historyswitch.isOn == false){
                //when history switch is off, take 20 measurements of temperature,co2,organic and humidity and put in 4 arrays seperately
                let str1 = NSString(format: "%.1f", data.temperature as CVarArg) as String
                ConnectLabel.text = str1
                tempHist.remove(at: 0)
                tempHist.append(data.temperature)
                let str2 = NSString(format: "%d", data.co2 as CVarArg) as String
                ConnectLabel2.text = str2
                CO2Hist.remove(at: 0)
                CO2Hist.append(data.co2)
                let str3 = NSString(format: "%d", data.organic as CVarArg) as String
                ConnectLabel3.text = str3   //*** Not yet added to the storyboard ***
                organicHist.remove(at: 0)
                organicHist.append(data.organic)
                let str4 = NSString(format: "%.1f", data.humidity as CVarArg) as String
                ConnectLabel4.text = String(str4.prefix(str4.count - 1))
                humidityHist.remove(at: 0)
                humidityHist.append(data.humidity)
                
                if (tempSwitch.isOn == true){
                    //when temperature switch is on,show the chart based on the temperature data
                    var elementArray = [
                        AASeriesElement()
                            .name("Temperature/°C")
                            .data(tempHist)
                            .toDic()!]
                    aaChartView.aa_onlyRefreshTheChartDataWithChartModelSeries(elementArray)
                }
                if(humanitySwitch.isOn == true){
                     //when humidity switch is on,show the chart based on the humidity data
                    var elementArray = [
                        AASeriesElement()
                            .name("humidty/%")
                            .data(humidityHist)
                            .toDic()!]
                    aaChartView.aa_onlyRefreshTheChartDataWithChartModelSeries(elementArray)
                }
                if(organicSwitch.isOn == true){
                     //when organic switch is on,show the chart based on the organic data
                    var elementArray = [
                        AASeriesElement()
                            .name("organic/ppb")
                            .data(organicHist)
                            .toDic()!]
                    aaChartView.aa_onlyRefreshTheChartDataWithChartModelSeries(elementArray)
                }
                if(co2Switch.isOn == true){
                     //when CO2 switch is on,show the chart based on the CO2 data
                    var elementArray = [
                        AASeriesElement()
                            .name("CO2/ppm")
                            .data(CO2Hist)
                            .toDic()!]
                    aaChartView.aa_onlyRefreshTheChartDataWithChartModelSeries(elementArray)
                }
            }else if(historyswitch.isOn == true){
                
                let str1 = NSString(format: "%.1f", data.temperature as CVarArg) as String
                ConnectLabel.text = str1
                tempHist.remove(at: 0)
                tempHist.append(data.temperature)
                
                var elementArray1 = [
                    AASeriesElement()
                        .name("Temperature/°C")
                        .data(tempHist)
                        .toDic()!]
                
                let str2 = NSString(format: "%d", data.co2 as CVarArg) as String
                ConnectLabel2.text = str2
                CO2Hist.remove(at: 0)
                CO2Hist.append(data.co2)
                
                var elementArray4 = [
                    AASeriesElement()
                        .name("CO2/ppm")
                        .data(CO2Hist)
                        .toDic()!]
                
                let str3 = NSString(format: "%d", data.organic as CVarArg) as String
                ConnectLabel3.text = str3   
                organicHist.remove(at: 0)
                organicHist.append(data.organic)
                
                var elementArray3 = [
                    AASeriesElement()
                        .name("organic/ppb")
                        .data(organicHist)
                        .toDic()!]
                
                let str4 = NSString(format: "%.1f", data.humidity as CVarArg) as String
                ConnectLabel4.text = String(str4.prefix(str4.count - 1))
                humidityHist.remove(at: 0)
                humidityHist.append(data.humidity)
                
                var elementArray2 = [
                    AASeriesElement()
                        .name("humidty/%")
                        .data(humidityHist)
                        .toDic()!]
            }
        }
        
        else if (topicRecieved == "Hot_Wings/history"){
            // when history arrives, parse history data to tempHist array and display depending on graph switches
            guard var historyData = try? JSONDecoder().decode(Measurements.self, from: messageRecieved.data(using: String.Encoding.utf8)!) else {
                print("Invalid data received")
                return
            }
            var elementArray1: [[String: AnyObject]]
            var elementArray2: [[String: AnyObject]]
            var elementArray3: [[String: AnyObject]]
            var elementArray4: [[String: AnyObject]]
            
                    
                var str1 = NSString(format: "%.1f", historyData.temperature as CVarArg) as String
                ConnectLabel.text = str1
                tempHist.remove(at: 0)
                tempHist.append(historyData.temperature)
                
                
                    
                var str2 = NSString(format: "%d", historyData.co2 as CVarArg) as String
                    ConnectLabel2.text = str2
                    CO2Hist.remove(at: 0)
                    CO2Hist.append(historyData.co2)
                    
                
                var str3 = NSString(format: "%d", historyData.organic as CVarArg) as String
                    ConnectLabel3.text = str3   
                    organicHist.remove(at: 0)
                    organicHist.append(historyData.organic)
                    
                
                    
                var str4 = NSString(format: "%.1f", historyData.humidity as CVarArg) as String
                    ConnectLabel4.text = String(str4.prefix(str4.count - 1))
                    humidityHist.remove(at: 0)
                    humidityHist.append(historyData.humidity)
                    
                
            
            elementArray1 = [
                AASeriesElement()
                    .name("Temperature/°C")
                    .data(tempHist)
                    .toDic()!]
            
            elementArray2 = [
                AASeriesElement()
                    .name("CO2/ppm")
                    .data(CO2Hist)
                    .toDic()!]
            
            elementArray3 = [
                AASeriesElement()
                    .name("organic/ppb")
                    .data(organicHist)
                    .toDic()!]
            
            elementArray4 = [
                AASeriesElement()
                    .name("humidty/%")
                    .data(humidityHist)
                    .toDic()!]
            
            if(historyswitch.isOn == true){
                if (tempSwitch.isOn == true){
                    aaChartView.aa_onlyRefreshTheChartDataWithChartModelSeries(elementArray1)
                }
                if(co2Switch.isOn == true){
                    aaChartView.aa_onlyRefreshTheChartDataWithChartModelSeries(elementArray2)
                }
                if(organicSwitch.isOn == true){
                    aaChartView.aa_onlyRefreshTheChartDataWithChartModelSeries(elementArray3)
                }
                if(humanitySwitch.isOn == true){
                    aaChartView.aa_onlyRefreshTheChartDataWithChartModelSeries(elementArray4)
                }
            }
            
        }
    }
    
    //initialize mqtt
    @objc func mqttsetting(){
        let clientID = "CocoaMQTT-" + String(ProcessInfo().processIdentifier)
        mqtt = CocoaMQTT(clientID: clientID, host: "m24.cloudmqtt.com", port: 18340)
        mqtt.username = "tctlhxmo"
        mqtt.password = "v1zfBxMko57N"
        mqtt.keepAlive = 60
        mqtt.delegate = self
        mqtt.cleanSession = true
        mqtt.allowUntrustCACertificate = true
        mqtt.autoReconnect = true
        mqtt.logLevel = .debug
        mqtt!.connect()
    }
    
    //for SSL connection
    func selfSignedSSLSetting(){
        let clientID = "CocoaMQTT-" + String(ProcessInfo().processIdentifier)
        mqtt = CocoaMQTT(clientID: clientID, host: "m24.cloudmqtt.com", port: 28340)
        mqtt!.username = "tctlhxmo"
        mqtt!.password = "v1zfBxMko57N"
        mqtt!.willMessage = CocoaMQTTWill(topic: "Hot_Wings/#", message: "dieout")
        mqtt!.keepAlive = 60
        mqtt!.delegate = self
        mqtt!.enableSSL = true
        mqtt!.cleanSession = true
        mqtt!.autoReconnect = true
        mqtt!.logLevel = .debug
        mqtt.allowUntrustCACertificate = true
        let clientCertArray = getClientCertFromP12File(certName: "client_3", certPassword: "19286124")
        var sslSettings: [String: NSObject] = [:]
        sslSettings[kCFStreamSSLCertificates as String] = clientCertArray
        mqtt!.sslSettings = sslSettings
        mqtt!.connect()
    }
    
    //get SSL client certification from p12 file
    func getClientCertFromP12File(certName: String, certPassword: String) -> CFArray? {
        // get p12 file path
        let resourcePath = Bundle.main.path(forResource: certName, ofType: "p12")
        
        guard let filePath = resourcePath, let p12Data = NSData(contentsOfFile: filePath) else {
            print("Failed to open the certificate file: \(certName).p12")
            return nil
        }
        
        // create key dictionary for reading p12 file
        let key = kSecImportExportPassphrase as String
        let options : NSDictionary = [key: certPassword]
        
        var items : CFArray?
        let securityError = SecPKCS12Import(p12Data, options, &items)
        
        guard securityError == errSecSuccess else {
            if securityError == errSecAuthFailed {
                print("ERROR: SecPKCS12Import returned errSecAuthFailed. Incorrect password?")
            } else {
                print("Failed to open the certificate file: \(certName).p12")
            }
            return nil
        }
        
        guard let theArray = items, CFArrayGetCount(theArray) > 0 else {
            return nil
        }
        
        let dictionary = (theArray as NSArray).object(at: 0)
        guard let identity = (dictionary as AnyObject).value(forKey: kSecImportItemIdentity as String) else {
            return nil
        }
        let certArray = [identity] as CFArray
        
        return certArray
    }
}



extension ViewController: CocoaMQTTDelegate {
    // Optional ssl CocoaMQTTDelegate
    func mqtt(_ mqtt: CocoaMQTT, didReceive trust: SecTrust, completionHandler: @escaping (Bool) -> Void) {
        TRACE("trust: \(trust)")
        /// Validate the server certificate
        ///
        /// Some custom validation...
        ///
        /// if validatePassed {
        ///     completionHandler(true)
        /// } else {
        ///     completionHandler(false)
        /// }
        completionHandler(true)
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didConnectAck ack: CocoaMQTTConnAck) {
        TRACE("ack: \(ack)")
        
        if ack == .accept {
            mqtt.subscribe("Hot_Wings/#", qos: CocoaMQTTQOS.qos1)
        }
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didStateChangeTo state: CocoaMQTTConnState) {
        TRACE("new state: \(state)")
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didPublishMessage message: CocoaMQTTMessage, id: UInt16) {
        TRACE("message: \(message.string?.debugDescription), id: \(id)")
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didPublishAck id: UInt16) {
        TRACE("id: \(id)")
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didReceiveMessage message: CocoaMQTTMessage, id: UInt16 ) {
        TRACE("message: \(message.string?.debugDescription), id: \(id)")
        
        //mqtt stores the received message in notification center
        let name = NSNotification.Name(rawValue: "MQTTMessageNotification")
        NotificationCenter.default.post(name: name, object: self, userInfo: ["message": message.string!, "topic": message.topic])
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didSubscribeTopic topic: String) {
        TRACE("topic: \(topic)")
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didUnsubscribeTopic topic: String) {
        TRACE("topic: \(topic)")
    }
    
    func mqttDidPing(_ mqtt: CocoaMQTT) {
        TRACE()
    }
    
    func mqttDidReceivePong(_ mqtt: CocoaMQTT) {
        TRACE("Received Pong")
    }
    
    func mqttDidDisconnect(_ mqtt: CocoaMQTT, withError err: Error?) {
        TRACE("\(err.debugDescription)")
    }
}

extension ViewController {
    func TRACE(_ message: String = "", fun: String = #function) {
        let names = fun.components(separatedBy: ":")
        var prettyName: String
        if names.count == 1 {
            prettyName = names[0]
        } else {
            prettyName = names[1]
        }
        
        if fun == "mqttDidDisconnect(_:withError:)" {
            prettyName = "didDisconect"
        }
        
        print("[TRACE] [\(prettyName)]: \(message)")
    }
}

extension ViewController: UITextFieldDelegate{
    //hide keyboard when return
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        speciesText.resignFirstResponder()
        return true
    }
}
