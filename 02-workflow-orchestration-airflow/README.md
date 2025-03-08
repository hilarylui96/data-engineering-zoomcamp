![Screenshot 2025-03-07 at 9 55 16 PM](https://github.com/user-attachments/assets/deb91a44-f28d-4b2e-b3bd-641faff32042)

1. Setting up Airflow in a Docker Container: https://www.youtube.com/watch?v=aTaytcxy2Ck&ab_channel=DatawithMarc
2. Mount Google Cloud credentials to Docker container in docker-compose.yaml
3. Create a .gitignore file and add the path of your credential json there to avoid pushing your credentials to the repo
4. Set Google Cloud connection via Airflow UI and set "Keyfile Path" to where the credentials json file is in the Docker container
5. Create requirement.txt and add the Python packages that you need
6. Create Dockerfile and configure it to pip install the packages listed in the requirements.txt
7. Modify docker-compose.yaml to build the image defined in the Dockerfile (comment out image: ${AIRFLOW_IMAGE_NAME:-apache/airflow:2.10.5} and add build .)

You can access your Docker Container / Airflow by clicking "Attach to Running Container" and select the Airflow Scheduler.
The pros of coding in the container is that there is auto-completion since Airflow is installed in the container but you might have to also install Python. 

Troubleshoot: 
- If you cannot use Bash / open the terminal in your container, Command + Shift + P > Terminal: Select Default Profile > select bin/bash
- if you cannot access Airflow UI, first check docker-ps to see the status of the webserver to confirm it is up and running. If it is, try to clear cache in your browser.
- If you run into a permission error when running pip install in your Dockerfile, it might be because the default user which is "airflow" does not have the permission to do so. Switch to user "root" and pip install and switch back to "airflow"

Tips:
- If you make changes to your Dockerfile and want to rebuild the image, you don't have to rebuild the image separately and rerun docker-compose.
- Just do docker-compose down && docker-compose up --build -d
- https://registry.astronomer.io/providers Great resource to look up Airflow providers and Operators
- Command + Shift + Space for displaying parameter for the function you are using
