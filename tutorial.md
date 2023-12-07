<walkthrough-metadata>
  <meta name="title" content="Edit Jumpstart Solution and deploy tutorial " />
   <meta name="description" content="Make it mine neos tutorial" />
  <meta name="component_id" content="1361081" />
  <meta name="unlisted" content="true" />
  <meta name="short_id" content="true" />
</walkthrough-metadata>

# Customize Generative AI Document Summarization Solution

This tutorial provides the steps for you to build your own proof of concept solution based on the deployed [Generative AI Document Summarization](https://console.cloud.google.com/products/solutions/details/generative-ai-document-summarization) Jump Start Solution (JSS) and deploy it. You can customize the Jump Start Solution (JSS) deployment by creating your own copy of the source code. You can modify the infrastructure and application code as needed and redeploy the solution with the changes.

The solution should be edited and deployed by one user at a time to avoid conflicts. Multiple users editing and updating the same deployment in the same GCP project can lead to conflicts.

## Know your solution

Here are the details of the Generative AI Document Summarization Jump Start Solution chosen by you.

Solution Guide: [here](https://cloud.google.com/architecture/ai-ml/generative-ai-document-summarization)

The code for the solution is avaiable at the following location
* Infrastructure code is present as part of <walkthrough-editor-open-file filePath="./main.tf">main.tf</walkthrough-editor-open-file>
* The Cloud Functions webhook is present under `./webhook`


## Explore or Edit the solution as per your requirement

The `entrypoint` function in the <walkthrough-editor-select-line filePath="./webhook/main.py" startLine="81" endLine="82" startCharacterOffset="0" endCharacterOffset="0">./webhook/main.py</walkthrough-editor-select-line> gets triggered when we send a document summarization request. This function is event driven and is called using Cloud Functions.

The terraform code for the solution is present in the `*.tf` files in the current directory.

As an example, you can edit <walkthrough-editor-select-line filePath="./webhook/main.py" startLine="164" endLine="165" startCharacterOffset="0" endCharacterOffset="0">./webhook/main.py</walkthrough-editor-select-line> and replace the value of `temperature` parameter to `0.9` in the call being made to the `predict_large_language_model` function in the `summarization_entrypoint` function. Increasing the temperature parameter leads to more diverse responses from the model.

NOTE: The changes in infrastructure may lead to reduction or increase in the incurred cost.

Please note: to open your recently used workspace:
* Go to the `File` menu.
* Select `Open Recent Workspace`.
* Choose the desired workspace.


---
**Automated deployment**

Execute the <walkthrough-editor-open-file filePath="./deploy_im.sh">deploy_im.sh</walkthrough-editor-open-file> script if you want an automated deployment to happen without following the full tutorial.
This step is optional and you can continue with the full tutorial if you want to understand the individual steps involved in the script.

```bash
./deploy_im.sh
```

## Gather the required information for intializing gcloud command

In this step you will gather the information required for the deployment of the solution.

---
**Project ID**

Use the following command to see the projectId:

```bash
gcloud config get project
```

```
Use above output to set the <var>PROJECT_ID</var>
```

---
**Deployment Region**

```
Provide the region (e.g. us-central1) where the top level deployment resources were created for the deployment <var>REGION</var>
```

---
**Deployment Name**

Run the following command to get the existing deployment name:
```bash
gcloud infra-manager deployments list --location <var>REGION</var> --filter="labels.goog-solutions-console-deployment-name:* AND labels.goog-solutions-console-solution-id:generative-ai-document-summarization"
```

```
Use the NAME value of the above output to set the <var>DEPLOYMENT_NAME</var>
```


## Deploy the solution


---
**Fetch Deployment details**
```bash
gcloud infra-manager deployments describe <var>DEPLOYMENT_NAME</var> --location <var>REGION</var>
```
From the output of this command, note down the input values provided in the existing deployment in the `terraformBlueprint.inputValues` section.

Also note the serviceAccount from the output of this command. The value of this field is of the form
```
projects/<var>PROJECT_ID</var>/serviceAccounts/<service-account>@<var>PROJECT_ID</var>.iam.gserviceaccount.com
```

```
Note <service-account> part and set the <var>SERVICE_ACCOUNT</var> value.
You can also set it to any exising service account.
```

---
**Assign the required roles to the service account**
```bash
while IFS= read -r role || [[ -n "$role" ]]
do \
gcloud projects add-iam-policy-binding <var>PROJECT_ID</var> \
  --member="serviceAccount:<var>SERVICE_ACCOUNT</var>@<var>PROJECT_ID</var>.iam.gserviceaccount.com" \
  --role="$role"
done < "roles.txt"
```

---
**Create Terraform input file**

Create an `input.tfvars` file in the current directory.

Find the sample content below and modify it by providing the respective details.
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

Execute the following command to trigger the re-deployment.
```bash
gcloud infra-manager deployments apply projects/<var>PROJECT_ID</var>/locations/<var>REGION</var>/deployments/<var>DEPLOYMENT_NAME</var> --service-account projects/<var>PROJECT_ID</var>/serviceAccounts/<var>SERVICE_ACCOUNT</var>@<var>PROJECT_ID</var>.iam.gserviceaccount.com --local-source="."     --inputs-file=./input.tfvars --labels="modification-reason=make-it-mine,goog-solutions-console-deployment-name=<var>DEPLOYMENT_NAME</var>,goog-solutions-console-solution-id=generative-ai-document-summarization,goog-config-partner=sc"
```

---
**Monitor the Deployment**

Execute the following command to get the deployment details.

```bash
gcloud infra-manager deployments describe <var>DEPLOYMENT_NAME</var> --location <var>REGION</var>
```

Monitor your deployment at [JSS deployment page](https://console.cloud.google.com/products/solutions/deployments?pageState=(%22deployments%22:(%22f%22:%22%255B%257B_22k_22_3A_22Labels_22_2C_22t_22_3A13_2C_22v_22_3A_22_5C_22modification-reason%2520_3A%2520make-it-mine_5C_22_22_2C_22s_22_3Atrue_2C_22i_22_3A_22deployment.labels_22%257D%255D%22))).

## Save your edits to the solution

Use any of the following methods to save your edits to the solution

---
**Download your solution in tar file**
* Click on the `File` menu
* Select `Download Workspace` to download the whole workspace on your local in compressed format.

---
**Save your solution to your git repository**

Set the remote url to your own repository
```bash 
git remote set-url origin [your-own-repo-url]
```

Review the modified files, commit and push to your remote repository branch.
<walkthrough-inline-feedback></walkthrough-inline-feedback>
