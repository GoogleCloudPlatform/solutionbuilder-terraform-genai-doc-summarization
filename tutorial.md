<walkthrough-metadata>
  <meta name="title" content="Edit Jumpstart Solution and deploy tutorial " />
  <meta name="description" content="Make it mine neos tutorial" />
  <meta name="component_id" content="1361081" />
  <meta name="short_id" content="true" />
</walkthrough-metadata>

# Customize a Generative AI Document Summarization solution

Learn how to build and deploy your own proof of concept based on the deployed [Generative AI Document Summarization](https://console.cloud.google.com/products/solutions/details/generative-ai-document-summarization) Jump Start Solution. You can customize the Jump Start Solution deployment by creating a copy of the source code. You can modify the infrastructure and application code as needed and redeploy the solution with the changes.

To avoid conflicts, only one user should modify and deploy a solution in a single Google Cloud project.

## Open cloned repository as workspace

Open the directory where the repository is cloned as a workspace in the editor, follow the steps based on whether you are using the Cloud Shell Editor in Preview Mode or Legacy Mode.

---
**Legacy Cloud Shell Editor**

1. Go to the `File` menu.
2. Select `Open Workspace`.
3. Choose the directory where the repository has been cloned. This directory is the current directory in the cloud shell terminal.

**New Cloud Shell Editor**

1. Go the hamburger icon located in the top left corner of the editor.
2. Go to the `File` Menu.
3. Select `Open Folder`.
4. Choose the directory where the repository has been cloned. This directory is the current directory in the cloud shell terminal.

## Before you begin

Before editing the solution, you should be aware of the following information:

* Cloud Functions webhook is present under `./webhook` directory. The `entrypoint` function in the <walkthrough-editor-select-line filePath="./webhook/main.py" startLine="81" endLine="82" startCharacterOffset="0" endCharacterOffset="0">./webhook/main.py</walkthrough-editor-select-line> gets triggered when we send a document summarization request. This function is event driven and is called using Cloud Functions.
* Terraform / infrastructure code is available in the `*.tf` files.

We also strongly recommend that you familiarize yourself with the three-tier web app solution by reading the [solution guide](https://cloud.google.com/architecture/application-development/generative-ai-document-summarization).

## Edit the solution

For example, edit <walkthrough-editor-select-line filePath="./webhook/main.py" startLine="164" endLine="165" startCharacterOffset="0" endCharacterOffset="0">./webhook/main.py</walkthrough-editor-select-line> and replace the value of `temperature` parameter to `0.9`. Increasing the temperature parameter leads to more diverse responses from the model.

NOTE: A change in the infrastructure code might cause a reduction or increase in the incurred cost.

---
**Create an automated deployment**

Optional: If you want to learn individual steps involved in the script, you can skip this step and continue with the rest of the tutorial. However, if you want an automated deployment without following the full tutorial, run the <walkthrough-editor-open-file filePath="./deploy_solution.sh">deploy_solution.sh</walkthrough-editor-open-file> script.

```bash
./deploy_solution.sh
```

## Gather information to initialize the deployment environment

---
**Project ID**

Get the Project ID:

```bash
gcloud config get project
```

```
Use the output to set the <var>PROJECT_ID</var>
```

---
**Deployment region**

```
For <var>REGION</var>, provide the region (e.g. us-central1) where you created the deployment resources.
```

---
**Deployment name**

```bash
gcloud infra-manager deployments list --location <var>REGION</var> --filter="labels.goog-solutions-console-deployment-name:* AND labels.goog-solutions-console-solution-id:generative-ai-document-summarization"
```

```
Use the output value of name to set the <var>DEPLOYMENT_NAME</var>
```

---

**Create the cloud storage bucket if it does not exist already**

Verify if the Cloud Storage bucket exists
```bash
gsutil ls gs://<var>PROJECT_ID</var>_infra_manager_staging
```

If the command returns an error indicating a non-existing bucket, create the bucket by running below command. Otherwise move on to the next step.
```bash
gsutil mb gs://<var>PROJECT_ID</var>_infra_manager_staging/
```

## Deploy the solution


---
**Fetch Deployment details**
```bash
gcloud infra-manager deployments describe <var>DEPLOYMENT_NAME</var> --location <var>REGION</var>
```
From the output, note down the following:
* The values of the existing deployment available in the `terraformBlueprint.inputValues` section.
* The service account. It is of the following form:

```
projects/<var>PROJECT_ID</var>/serviceAccounts/<service-account>@<var>PROJECT_ID</var>.iam.gserviceaccount.com
```

```
Note <service-account> part and set the <var>SERVICE_ACCOUNT</var> value.
You can also set it to any existing service account.
```

---
**Assign the required roles to the service account**
```bash
CURRENT_POLICY=$(gcloud projects get-iam-policy <var>PROJECT_ID</var> --format=json)
MEMBER="serviceAccount:<var>SERVICE_ACCOUNT</var>@<var>PROJECT_ID</var>.iam.gserviceaccount.com"
while IFS= read -r role || [[ -n "$role" ]]
do \
if echo "$CURRENT_POLICY" | jq -e --arg role "$role" --arg member "$MEMBER" '.bindings[] | select(.role == $role) | .members[] | select(. == $member)' > /dev/null; then \
    echo "IAM policy binding already exists for member ${MEMBER} and role ${role}"
else \
    gcloud projects add-iam-policy-binding <var>PROJECT_ID</var> \
    --member="$MEMBER" \
    --role="$role" \
    --condition=None
fi
done < "roles.txt"
```

---
**Create a terraform input file**

Create an `input.tfvars` file in the current directory with the following contents:

```
region="us-central1"
project_id = "<var>PROJECT_ID</var>"
bucket_name="genai-webhook"
webhook_name="webhook"
webhook_path="webhook"
gcf_timeout_seconds=900
time_to_enable_apis="180s"
labels = {
  "goog-solutions-console-deployment-name" = "<var>DEPLOYMENT_NAME</var>",
  "goog-solutions-console-solution-id" = "generative-ai-document-summarization"
}
```

---
**Deploy the solution**

Trigger the re-deployment.
```bash
gcloud infra-manager deployments apply projects/<var>PROJECT_ID</var>/locations/<var>REGION</var>/deployments/<var>DEPLOYMENT_NAME</var> --service-account projects/<var>PROJECT_ID</var>/serviceAccounts/<var>SERVICE_ACCOUNT</var>@<var>PROJECT_ID</var>.iam.gserviceaccount.com --local-source="."     --inputs-file=./input.tfvars --labels="modification-reason=make-it-mine,goog-solutions-console-deployment-name=<var>DEPLOYMENT_NAME</var>,goog-solutions-console-solution-id=generative-ai-document-summarization,goog-config-partner=sc"
```

---
**Monitor the deployment**

Get the deployment details.

```bash
gcloud infra-manager deployments describe <var>DEPLOYMENT_NAME</var> --location <var>REGION</var>
```

Monitor your deployment at [Solution deployments page](https://console.cloud.google.com/products/solutions/deployments?pageState=(%22deployments%22:(%22f%22:%22%255B%257B_22k_22_3A_22Labels_22_2C_22t_22_3A13_2C_22v_22_3A_22_5C_22modification-reason%2520_3A%2520make-it-mine_5C_22_22_2C_22s_22_3Atrue_2C_22i_22_3A_22deployment.labels_22%257D%255D%22))).

## Save your edits to the solution

Use any of the following methods to save your edits to the solution

---
**Download the solution**

To download your solution, in the `File` menu, select `Download Workspace`. The solution is downloaded in a compressed format.


---
**Save the solution to your Git repository**

Set the remote url to your Git repository
```bash 
git remote set-url origin [git-repo-url]
```

Review the modified files, commit and push to your remote repository branch.

## Delete the deployed solution

Optional: Use one of the below options in case you want to delete the deployed solution

* Go to [Solution deployments page](https://console.cloud.google.com/products/solutions/deployments?pageState=(%22deployments%22:(%22f%22:%22%255B%257B_22k_22_3A_22Labels_22_2C_22t_22_3A13_2C_22v_22_3A_22_5C_22modification-reason%2520_3A%2520make-it-mine_5C_22_22_2C_22s_22_3Atrue_2C_22i_22_3A_22deployment.labels_22%257D%255D%22))).
* Click on the link under "Deployment name". It will take you to the deployment details page for the solution.
* Click on the "DELETE" button on the top left corner of the page
<walkthrough-inline-feedback></walkthrough-inline-feedback>
