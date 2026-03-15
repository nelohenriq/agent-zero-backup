---
name: find-skills
description: Search and discover AI agent skills from the Vercel AI/Skills ecosystem.
version: 1.0.0
author: Agent Zero (Ported)
tags: [meta, discovery, skills]
---

# find-skills

Search and discover AI agent skills from the Vercel AI/Skills ecosystem and more.

## Usage

Use this skill to find new capabilities when you don't know how to perform a specific task.

## Procedures

### Search for skills
Run the following command to search for skills based on a query:
bash
npx skills find <query>


### Install a discovered skill
Once a skill is found (e.g., owner/repo@skill), you can attempt to install it using:
bash
npx skills add <owner/repo@skill>

*Note: Installation may require manual intervention or porting to Agent Zero format.*
