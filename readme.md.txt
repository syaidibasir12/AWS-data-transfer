# 🎧 ContactSpace Recording Automation to AWS S3

Automated script to fetch audio recordings from ContactSpace API and upload them securely to AWS S3. Designed for scalability, easy configuration, and minimal manual intervention.

---

## 🔧 Features

- ✅ Automatically downloads daily call recordings from ContactSpace
- 📁 Uploads files to structured AWS S3 folders (e.g., `recordings/june_2025/`)
- 🔍 Skips files that already exist in S3 to prevent duplicates
- 🔐 Uses `.env` file for secure and clean credential handling
- 🗑️ Deletes local files after successful upload to save disk space
- 🧩 Easy to configure for any date range

---

-Created by Syaidinsem, Intern Awesome 2025.

