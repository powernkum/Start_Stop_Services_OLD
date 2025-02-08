## This script starts services in the root folder and all services in a folder/multiple folders on arcgis server
# For Http calls
import httplib, urllib, json
# For system tools
import sys
# For reading passwords without echoing
import getpass


# defining the required variables with the admin logins
username = ''
password = ''
serverName = ''
serverPort = 6080
stopOrStart = ""
params = ""
headers = ""

# Defines the entry point into the script
def main(username,password,serverName,serverPort,stopOrStart):
    # Print some info
    print "This tool is a sample script that stops or starts all services in a folder."
    # using the switch case in python to consider both root directory and folder
    # We're implementing the switch statement below by creating a dictionary of function names as values. In this case, the services_directory is a dictionary of function names, and not strings.
        
    # defining the root function to return the root value
    def ROOT():
        return "ROOT"
        # defining the folder function to return the folder variable
    def folder():
        return "folder"
        
    global services_directory # defining the dictionary so it can be used outside the function
    #global stopOrStart 
    services_directory = {
    1: ROOT,
    2: folder
    }
 
    def root_folder(argument):
        # Get the function from services_directory dictionary
        func = services_directory.get(argument, "nothing")
        # Execute the function
        return func()

    # calling the function for the second case where the services are in the folder
    folder = root_folder(2) 
    stopOrStart = 'START'
    # calling function to construct urls after reading folder, get token etc
    constructurlfunction(username, password, serverName, serverPort,stopOrStart,params,headers,folder)
    
    # calling the function for the first case where the services are in the root directory
    folder = root_folder(1) 
    stopOrStart = 'START'
    #nb: the switch case can be changed ie. changing the value of the services_directory dictionary for key 1 to folder so that the new value will be the function call for folder. e.g. root_folder[1]=two
    # calling function to construct urls after reading folder, get token etc
    constructurlfunction(username, password, serverName, serverPort,stopOrStart,params,headers,folder)
         
#function designed to construct urls after reading folder, get token etc
def constructurlfunction(username, password, serverName, serverPort,stopOrStart,params,headers,folder):
    # defining the list object to contain/host the folders
    global folderURL
    global token
    global list_folders
    global data
    # Check to make sure stop/start parameter is a valid value
   # if str.upper(stopOrStart) != "START" and str.upper(stopOrStart) != "STOP":
    #    print "Invalid STOP/START parameter entered"
     #   return
    
    # Get a token
    token = getToken(username, password, serverName, serverPort)
    if token == "":
        print "Could not generate a token with the username and password provided."
        return
                
    # This request only needs the token and the response formatting parameter 
    params = urllib.urlencode({'token': token, 'f': 'json'})
    
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    # Construct URL to read folder
    if str.upper(folder) == "ROOT":
        folder = ""
        folderURL = "http://.............com/arcgis/admin/services/" + folder
        
        # calling function to start/stop services in the root folder
        servicestartstop_root(params,headers,serverName,serverPort,folderURL,stopOrStart,folder)
                
    else:
        folderURL = "http://................com/arcgis/admin/services/" 
        httpConn = httplib.HTTPConnection(serverName, serverPort)
        httpConn.request("POST", folderURL, params, headers)
    
        # Read response
        response = httpConn.getresponse()
        if (response.status != 200):
                httpConn.close()
                print "Could not read folder information."
                return
        else:
                data = response.read()
                print "root data"
        
                # Check that data returned is not an error object
                if not assertJsonSuccess(data):          
                        print "Error when reading folder information. " + str(data)
                else:
                        print "Processed folder information successfully. Now processing services..."

                # Deserialize response into Python object
                dataObj = json.loads(data)
                httpConn.close()

                length = len(dataObj['folders']) # defining the length of the object
                list_folders =  [0]*length
                x =0 # initializing the the variable x
                for item in dataObj['folders']: # looping through the folders
                    list_folders[x] = item
                    x = x+1
                    print "folder",item
        list_folders.remove('System') # removing the system folder from the list
        list_folders.remove('Utilities') # removing the utilities folder from the list
         
        folder = ""
        # Connect to URL and post parameters
        if len(list_folders) > 1:
            for item in list_folders:
                folder =  str(item) # assign item to the folder
                folderURL = folderURL + folder # recreate the folder url
                print "folderurl",folderURL
                # calling function to start/stop services in the folders, subfolders residing in the services directory
                servicestartstop_folders(params,headers,serverName,serverPort,folderURL,stopOrStart,folder)
                folderURL = "http://................com/arcgis/admin/services/" 
    

# function to start/stop services in the root folder #1
def servicestartstop_root(params,headers,serverName,serverPort,folderURL,stopOrStart,folder):
    # Connect to URL and post parameters    
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", folderURL, params, headers)
    
    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print "Could not read folder information."
        return
    else:
        data = response.read()
        print "root data"
        
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):          
            print "Error when reading folder information. " + str(data)
        else:
            print "Processed folder information successfully. Now processing services..."

        # Deserialize response into Python object
        dataObj = json.loads(data)
        httpConn.close()
                        
            # Loop through each service in the folder and stop or start it    
        for item in dataObj['services']:
            fullSvcName = item['serviceName'] + "." + item['type']
            print fullSvcName
            # Construct URL to stop or start service, then make the request                
            stopOrStartURL = "http://................com/arcgis/admin/services/" + folder + fullSvcName + "/" + stopOrStart
            httpConn.request("POST", stopOrStartURL, params, headers)
            
            # Read stop or start response
            stopStartResponse = httpConn.getresponse()
            if (stopStartResponse.status != 200):
                httpConn.close()
                print "Error while executing stop or start. Please check the URL and try again."
                return
            else:
                stopStartData = stopStartResponse.read()
                
                # Check that data returned is not an error object
                if not assertJsonSuccess(stopStartData):
                    if str.upper(stopOrStart) == "START":
                        print "Error returned when starting service " + fullSvcName + "."
                    else:
                        print "Error returned when stopping service " + fullSvcName + "."

                    print str(stopStartData)
                    
                else:
                    print "Service " + fullSvcName + " processed successfully."

            httpConn.close()
        return


#function to start/stop services in the folders #2
def servicestartstop_folders(params,headers,serverName,serverPort,folderURL,stopOrStart,folder):
    # calling the list_folders object and looping through each of the folders
    global data

    # This request only needs the token and the response formatting parameter 
    params = urllib.urlencode({'token': token, 'f': 'json'})
    
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    # Connect to URL and post parameters    
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    print "httpConn", httpConn
    httpConn.request("POST", folderURL, params, headers)
    
    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print "Could not read folder information."
        return
    else:
        data = response.read()
        print "folder data"
        
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):          
            print "Error when reading folder information. " + str(data)
        else:
            print "Processed folder information successfully. Now processing services..."

        # Deserialize response into Python object
        dataObj = json.loads(data)
        httpConn.close()
        
        # Loop through each service in the folder and stop or start it    
        for item in dataObj['services']:
            fullSvcName = item['serviceName'] + "." + item['type']
            print "fullsvname",fullSvcName
            
            # Construct URL to stop or start service, then make the request                
            stopOrStartURL = "http://.....................com/arcgis/admin/services/" + folder + "/" + fullSvcName + "/" + stopOrStart
            httpConn.request("POST", stopOrStartURL, params, headers)
            
            # Read stop or start response
            stopStartResponse = httpConn.getresponse()
            if (stopStartResponse.status != 200):
                httpConn.close()
                print "Error while executing stop or start. Please check the URL and try again."
                return
            else:
                stopStartData = stopStartResponse.read()
                
                # Check that data returned is not an error object
                if not assertJsonSuccess(stopStartData):
                    if str.upper(stopOrStart) == "START":
                        print "Error returned when starting service " + fullSvcName + "."
                    else:
                        print "Error returned when stopping service " + fullSvcName + "."

                    print str(stopStartData)
                    
                else:
                    print "Service " + fullSvcName + " processed successfully."

            httpConn.close()
            folderURL = "http://.......com/arcgis/admin/services/"  # recreate the initial folder url to start the loop again
        return
        
            
 

# A function to generate a token given username, password and the adminURL.
def getToken(username, password, serverName, serverPort):
    # Token URL is typically http://server[:port]/arcgis/admin/generateToken
    tokenURL = "http://.........com/arcgis/admin/generateToken"
    
    params = urllib.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json'})
    
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    # Connect to URL and post parameters
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", tokenURL, params, headers)
    
    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print "Error while fetching tokens from admin URL. Please check the URL and try again."
        return
    else:
        data = response.read()
        httpConn.close()
        
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):            
            return
        
        # Extract the token from it
        token = json.loads(data)        
        return token['token']            
        

# A function that checks that the input JSON object 
#  is not an error object.
def assertJsonSuccess(data):
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        print "Error: JSON object returns an error. " + str(obj)
        return False
    else:
        return True
    
        
# Script start
"""
if __name__ == "__main__":
    sys.exit(main(sys.argv[5:]))
    """
main(username,password,serverName,serverPort,stopOrStart)
