# ATS Scorer Knowledge Base

Welcome to the central node of the ATS Scorer system. This graph maps out the entire architecture from the entry point down to the micro-functions.

## Core Services
- [[Frontend Application]]
- [[Backend Application]]

## Data Flow
When a user accesses the [[Frontend Application]], they interact with the [[page.tsx]] module which handles state and component orchestration. The data is then submitted to the [[Backend Application]] via the [[api.ts]] service layer.

The [[Backend Application]] uses [[main.py]] as its primary router, passing requests into the [[pipeline.py]] processing core.
