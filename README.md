# Prompt Optimisation and Evaluation

In the pursuit of transitioning language models from experimental stages to production-ready workloads, the evaluation phase emerges as an indispensable component of the prompt engineering and optimization process. It is through rigorous evaluation that prompt engineers can ensure the highest levels of accuracy, performance, and safety, thereby instilling confidence in the deployment of this technology.

# Target audience and content

This hands-on workshop aimed at Prompt Engineers and Generative AI application developers, provides an overview of the prompt optimisation and evaluation process through the use of various libraries either from Amazon Bedrock or open source libraries.

It covers important steps and components of the evaluation pipeline including:
- Creation of the test cases including edge cases
- Groundtruth data generation
- Prompt management
- Prompt Evaluation (Metrics and Scoring)
- RAG Evaluation
- Agents Trajectory Evaluation
- Observability

The workshop also go through the use of various frameworks like langfuse, langchain, langgraph, RAGAS and how they can be leveraged throughout the process.

# Notebooks description

0-preparation-synthetic_data - Call centre transcripts and FAQ generation

1-preparation-bedrock_kb_creation_load - VectorDB Knowledge base creation in Amazon Bedrock using FAQs

2-prompt_management - Summarisation/Extraction/Classification prompt definition in Amazon Bedrock Prompt Management

3-groundtruth_data_generation - Groundtruth data (question, context, answer) generation using reflection for the 3 use cases

4-evaluation - Evaluation of the 3 use cases through different libraries and metrics incl. safety ones

5-rag_evaluation_w_ragas - Evaluation of our RAG KB using the RAGAS library

6-agent_evaluation - Evaluation of an Agent's trajectory using Langchain

7-observability_w_langfuse - Observability and tracing features overview of langfuse

8-notebook_clean_up - deletion of AWS related resources (KB, IAM policies/roles, etc)

# 3rd party libraries used

https://github.com/huggingface/evaluate/ (Apache License 2.0)

https://github.com/explodinggradients/ragas  (Apache License 2.0)

https://github.com/langfuse/langfuse (MIT Expat)

https://github.com/langchain-ai/langchain (MIT License)

https://github.com/langchain-ai/langgraph (MIT License)

# Permissions

To run through these notebooks, you will need to ensure that your SageMaker execution role or your AWS CLI user has the necessary permissions/policies. 

See below a list of policies to attach to run the workshop: 
- IAMFullAccess, 
- AmazonBedrockFullAccess, 
- AmazonOpenSearchServiceFullAccess

As well as the following policy for OpenSearchServerless:

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "aoss:*",
                "Resource": "*"
            }
        ]
    }

Note that these policies are very permissive for the sake of simplicity in running the workshop, but they should be reviewed and minimized for production scenarios.

The workshop has been developed and tested in the following environments:

    Region: us-east-1
    Tested with Python 3.12.4 on Visual Studio with AWS CLI and AWS plugin configured