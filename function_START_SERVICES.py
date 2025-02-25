## This script starts services in the root folder and all services in a folder/multiple folders on ArcGIS Server.

# Import necessary modules
import httplib, urllib, json  # For HTTP requests
import sys  # For system operations
import getpass  # For secure password input

# Define global variables for authentication and server details
username = ''   # ArcGIS Server admin username
password = ''   # ArcGIS Server admin password
serverName = '' # ArcGIS Server hostname or IP
serverPort = 6080  # ArcGIS Server port (default: 6080)
stopOrStart = ""  # Action to perform (START or STOP)
params = ""  # Parameters for HTTP requests
headers = ""  # Headers for HTTP requests


def main(username, password, serverName, serverPort, stopOrStart):
    """
    Main function to manage services in the ArcGIS server.
    It starts or stops services in both the root folder and within specified folders.

    Args:
        username (str): Admin username for ArcGIS Server
        password (str): Admin password for ArcGIS Server
        serverName (str): ArcGIS Server hostname
        serverPort (int): ArcGIS Server port
        stopOrStart (str): Action to perform (START or STOP)
    """
    
    print("This tool is a sample script that stops or starts all services in a folder.")

    # Define a dictionary-based switch case to differentiate between root directory and folder
    def ROOT():
        """Returns a string indicating the root directory."""
        return "ROOT"

    def folder():
        """Returns a string indicating a folder operation."""
        return "folder"

    # Define a dictionary mapping service directory types to corresponding functions
    global services_directory
    services_directory = {
        1: ROOT,
        2: folder
    }

    def root_folder(argument):
        """
        Function to determine whether to process root or folder services.

        Args:
            argument (int): Key to select between root (1) or folder (2).
        
        Returns:
            function: Corresponding function reference.
        """
        func = services_directory.get(argument, "nothing")
        return func()

    # Process folder services first
    folder = root_folder(2)
    stopOrStart = 'START'
    constructurlfunction(username, password, serverName, serverPort, stopOrStart, params, headers, folder)

    # Process root services next
    folder = root_folder(1)
    stopOrStart = 'START'
    constructurlfunction(username, password, serverName, serverPort, stopOrStart, params, headers, folder)


def constructurlfunction(username, password, serverName, serverPort, stopOrStart, params, headers, folder):
    """
    Constructs URLs for service operations and manages authentication.

    Args:
        username (str): ArcGIS Server admin username
        password (str): ArcGIS Server admin password
        serverName (str): ArcGIS Server hostname
        serverPort (int): ArcGIS Server port
        stopOrStart (str): Action to perform (START or STOP)
        params (str): Query parameters for the HTTP request
        headers (dict): Headers for the HTTP request
        folder (str): Target folder for service operations
    """

    global folderURL, token, list_folders, data

    # Generate a token for authentication
    token = getToken(username, password, serverName, serverPort)
    if token == "":
        print("Could not generate a token with the username and password provided.")
        return

    # Encode parameters for authentication
    params = urllib.urlencode({'token': token, 'f': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    # Construct the folder URL for service management
    if str.upper(folder) == "ROOT":
        folder = ""
        folderURL = "http://.............com/arcgis/admin/services/" + folder
        servicestartstop_root(params, headers, serverName, serverPort, folderURL, stopOrStart, folder)
    else:
        folderURL = "http://................com/arcgis/admin/services/"
        httpConn = httplib.HTTPConnection(serverName, serverPort)
        httpConn.request("POST", folderURL, params, headers)

        # Process response
        response = httpConn.getresponse()
        if response.status != 200:
            httpConn.close()
            print("Could not read folder information.")
            return

        data = response.read()
        print("root data")

        if not assertJsonSuccess(data):
            print("Error when reading folder information.", str(data))
        else:
            print("Processed folder information successfully. Now processing services...")

        dataObj = json.loads(data)
        httpConn.close()

        # Retrieve folder names
        list_folders = [folder for folder in dataObj['folders'] if folder not in ('System', 'Utilities')]

        # Process services within folders
        for folder in list_folders:
            folderURL += folder
            print("folderurl", folderURL)
            servicestartstop_folders(params, headers, serverName, serverPort, folderURL, stopOrStart, folder)
            folderURL = "http://................com/arcgis/admin/services/"


def getToken(username, password, serverName, serverPort):
    """
    Generates an authentication token for ArcGIS Server.

    Args:
        username (str): ArcGIS Server admin username
        password (str): ArcGIS Server admin password
        serverName (str): ArcGIS Server hostname
        serverPort (int): ArcGIS Server port

    Returns:
        str: Authentication token
    """

    tokenURL = "http://.........com/arcgis/admin/generateToken"
    params = urllib.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", tokenURL, params, headers)

    response = httpConn.getresponse()
    if response.status != 200:
        httpConn.close()
        print("Error while fetching tokens from admin URL. Please check the URL and try again.")
        return

    data = response.read()
    httpConn.close()

    if not assertJsonSuccess(data):
        return

    token = json.loads(data)
    return token['token']


def assertJsonSuccess(data):
    """
    Validates that the response JSON object is not an error.

    Args:
        data (str): JSON response data

    Returns:
        bool: True if valid, False if an error occurs.
    """

    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        print("Error: JSON object returns an error.", str(obj))
        return False
    return True


# Start the script execution
"""
if __name__ == "__main__":
    sys.exit(main(sys.argv[5:]))
    """
main(username, password, serverName, serverPort, stopOrStart)
