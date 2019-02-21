//
//  GraphingController.swift
//  hangge_2287
//
//  Created by ooo on 2019/2/13.
//  Copyright © 2019 hangge. All rights reserved.
//

import UIKit

class GraphingController: UIViewController {
    
    /* This module is NOT used in the final application */
    @IBOutlet weak var scrollView: UIScrollView!
    @IBOutlet weak var label: UILabel!
    override func viewDidLoad() {
        super.viewDidLoad()
        scrollView.isPagingEnabled = true
        let temp_page = pageSetup(identifier: "Temperature")
        let humid_page = pageSetup(identifier: "Humidity")
        let co2_page = pageSetup(identifier: "CO2")
        let organic_page = pageSetup(identifier: "Organic")
        label.text = "test"
    }
    
    private func pageSetup(identifier: String)->GraphingController{
        let page = storyboard!.instantiateViewController(withIdentifier: identifier) as! GraphingController
        page.view.translatesAutoresizingMaskIntoConstraints = false
        scrollView.addSubview(page.view)
        page.didMove(toParent: self)
        return page
    }
    

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */

}
