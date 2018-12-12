#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Lists last released/completed tracl for a given app."""
# Can be used like:
# python getTrackVersionName --track production --package_name bla.bla.bla
# output: track: production, name: 0.2.1, status: completed
# if interested only in the name ( for code push ) pipe it | awk ':w{print $4}'

# install libs: pip install --upgrade google-api-python-client oauth2client

import argparse

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


# Declare command-line flags.
argparser = argparse.ArgumentParser()
argparser.add_argument('--track',
                       help='The track name. One of: production, beta, alpha, internal')
argparser.add_argument('--package_name',
                       help='The package name. Example: app.barker')

def get_service(api_name, api_version, scopes, key_file_location):
    """Get a service that communicates to a Google API.

    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.

    Returns:
        A service that is connected to the specified API.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            key_file_location, scopes=scopes)

    # Build the service object.
    service = build(api_name, api_version, credentials=credentials)

    return service


def main():
    # Define the auth scopes to request.
    scope = 'https://www.googleapis.com/auth/androidpublisher'
    # location of the google-json-key service account
    key_file_location = '../android/secret/google-json-key.json'

    # Process flags and read their values.
    flags = argparser.parse_args()

    package_name = flags.package_name if flags.package_name else 'barking.app'
    check_track = flags.track if flags.track else 'production'

    # Authenticate and construct service.
    service = get_service(
            api_name='androidpublisher',
            api_version='v3',
            scopes=[scope],
            key_file_location=key_file_location)
    try:

      # create an empty edit to get access to edit_id used in subsequent requests
      edit_request = service.edits().insert(body={}, packageName=package_name)

      result = edit_request.execute()
      edit_id = result['id']


      # api reference https://developers.google.com/android-publisher/api-ref/edits/tracks#resource
      tracks_result = service.edits().tracks().list(
          editId=edit_id, packageName=package_name).execute()

      for track in tracks_result['tracks']:
        if track['track'] == check_track:
          for release in track['releases']:
            if release['status'] == 'completed': # interested only in completed rollouts
              print ('track: %s name: %s status: %s' % ( track['track'], release['name'], release['status']))


    except client.AccessTokenRefreshError:
      print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')




if __name__ == '__main__':
    main()
