/**
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

output "neos_walkthrough_url" {
  value       = "https://console.cloud.google.com/products/solutions/deployments?walkthrough_id=panels--sic--document-summarization-gcf_tour"
  description = "The URL to launch the in-console tutorial for the Generative AI Document Summarization solution"
}

output "genai_doc_summary_colab_url" {
  value       = "https://colab.research.google.com/github/GoogleCloudPlatform/terraform-google-gen-ai-document-summarization/blob/main/notebook/gen_ai_jss.ipynb"
  description = "The URL to launch the notebook tutorial for the Generateive AI Document Summarization Solution"
}
