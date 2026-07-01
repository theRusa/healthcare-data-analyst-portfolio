# How to put this portfolio on GitHub

A one-time setup, ~10 minutes. Two routes: the GitHub Desktop app (easiest, no terminal) or the command line.

---

## Before you start
- Create a free account at https://github.com if you don't have one.
- Decide on a repo name. `healthcare-data-analyst-portfolio` reads well to recruiters.
- Keep the repo **Public** so people can see your work.

---

## Option A — GitHub Desktop (no command line)

1. Download and install **GitHub Desktop**: https://desktop.github.com
2. Open it and sign in to your GitHub account.
3. `File → Add Local Repository…` and choose this folder:
   `~/Claude/Projects/Portfolio`
4. It will say "this directory is not a Git repository" — click **Create a repository** here.
   - Name: `healthcare-data-analyst-portfolio`
   - Leave the rest as-is and click **Create Repository**.
5. You'll see all the files listed as changes. In the bottom-left box, type a summary like `Initial commit — 3 healthcare analytics projects`, then click **Commit to main**.
6. Click **Publish repository** (top bar). Make sure **"Keep this code private"** is *unchecked*, then publish.

Done — your work is now on GitHub. To share, copy the URL: `https://github.com/<your-username>/healthcare-data-analyst-portfolio`

---

## Option B — Command line (Terminal)

First time only, set your identity:
```bash
git config --global user.name "Maja Dosevska"
git config --global user.email "mdosevska@gmail.com"
```

Then, from this folder:
```bash
cd ~/Claude/Projects/Portfolio
git init
git add .
git commit -m "Initial commit — 3 healthcare analytics projects"
```

Create the empty repo on GitHub (via the website: **New repository**, name it, Public, **don't** add a README/license since you already have them). Then connect and push — GitHub shows you these exact two lines; they look like:
```bash
git remote add origin https://github.com/<your-username>/healthcare-data-analyst-portfolio.git
git branch -M main
git push -u origin main
```
If prompted to authenticate, use a **Personal Access Token** (GitHub → Settings → Developer settings → Personal access tokens) as the password, or install the GitHub CLI (`gh auth login`).

---

## After it's up — make it shine

- **Pin the repo** to your profile: GitHub profile → Customize your pins → select it.
- **Add a description** at the top of the repo: *"Three end-to-end healthcare analytics projects — SQL, Excel, and Power BI. Synthetic data."*
- **Add topics** (gear icon next to About): `data-analysis`, `sql`, `healthcare`, `power-bi`, `excel`, `portfolio`.
- **Put the link on your resume and LinkedIn.** The main `README.md` renders automatically as the landing page, dashboard image and all.

## A note on the big files
The Excel workbooks (~a few hundred KB each) and dashboard PNGs are fine to commit — they're small. The `.gitignore` already excludes temp/lock files. You do **not** need Git LFS for anything here.
