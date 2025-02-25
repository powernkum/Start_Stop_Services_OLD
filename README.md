# **ArcGIS Server Service Management**
This repository contains two scripts designed to **start** and **stop** ArcGIS services in both the root directory and specified folders on an ArcGIS Server using the REST API.

## **Overview**
- **`start_services.py`** - Starts all services in the root directory and selected folders.  
- **`stop_services.py`** - Stops all services in the root directory and selected folders.  

These scripts interact with the ArcGIS Server REST API to manage services automatically. They use HTTP requests to authenticate, retrieve available services, and perform the desired start/stop actions.

---

## **Prerequisites**
Before using these scripts, ensure you have the following:  
- A working installation of `Python 2.7`  
- Access to an `ArcGIS Server with administrative credentials` 
- Required Python libraries (**`httplib`**, **`urllib`**, **`json`**)  

---

## **Installation**
1. **Clone this repository**:
   ```bash
   git clone https://github.com/your-username/arcgis-service-management.git
   cd arcgis-service-management
   ```
2. **Ensure Python dependencies are installed**:
   ```bash
   pip install requests
   ```
   (If replacing `httplib` with `requests`)

---

## **Usage**
Each script requires authentication details (`username`, `password`, `serverName`, `serverPort`) and performs actions on services.

### **Start Services**
To start all services:
```bash
python start_services.py
```

### **Stop Services**
To stop all services:
```bash
python stop_services.py
```

---

## **Configuration**
Before running the scripts, update the following **variables** inside the `.py` files:

```python
# Define server authentication details
username = "your_admin_username"
password = "your_admin_password"
serverName = "your_arcgis_server_url"
serverPort = 6080  # Default port for ArcGIS Server
```

Ensure that the correct credentials are provided to avoid authentication errors.

---

## **How It Works**
Each script follows these steps:
1. Generates an authentication token using the ArcGIS REST API.  
2. Retrieves a list of services from the ArcGIS Server.  
3. Loops through all services in the root folder and specific subfolders.  
4. Executes the start/stop command via an HTTP request.  
5. Verifies the success of the operation and logs the results.

---

## **Example Output**
### **Start Services Output**
```
This tool is a sample script that starts all services in a folder.

Processed folder information successfully. Now processing services...
Service MyMapService.MapServer processed successfully.
Service MyGeocodeService.GeocodeServer processed successfully.
```

### **Stop Services Output**
```
This tool is a sample script that stops all services in a folder.

Processed folder information successfully. Now processing services...
Service MyMapService.MapServer stopped successfully.
Service MyGeocodeService.GeocodeServer stopped successfully.
```

---

## **Error Handling**
If the script fails to authenticate:
```
Could not generate a token with the username and password provided.
```
**Solution:** Ensure your credentials are correct and that the ArcGIS Server is reachable.

If a service fails to start or stop:
```
Error returned when starting/stopping service MyMapService.
```
**Solution:** Check whether the service is running and if the script has admin privileges.

---