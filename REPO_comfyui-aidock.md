Generated on Tuesday, 24 June 2025 at 06:18 AM

This file is a merged representation of a subset of the codebase, containing files not matching ignore patterns, combined into a single document by Repomix.
The content has been processed where line numbers have been added, content has been formatted for parsing in markdown style.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.
- Pay special attention to the Repository Description. These contain important context and guidelines specific to this project.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching these patterns are excluded: .my_docs, .env, build, venv, .git, output, node_modules, my_output, __pycache__, .venv
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Line numbers have been added to the beginning of each line
- Content has been formatted for parsing in markdown style

## Additional Info
### User Provided Header
🧠 Optimized Crawl4AI MCP Repo Snapshot for LLMs - comfyui-aidock

# Directory Structure
```
.github/FUNDING.yml
.github/workflows/build-env.yml
.github/workflows/clear-cache.yml
.github/workflows/delete-old-images.yml
.github/workflows/delete-untagged-images.yml
.github/workflows/docker-build.yml
.gitignore
config/provisioning/animated.sh
config/provisioning/default.sh
config/provisioning/flux.sh
config/provisioning/get-models-sd-official.sh
config/provisioning/sd3.sh
config/provisioning/seargedp-seargesdxl.sh
config/workflows/flux-comfyui-example.json
docker-compose.yaml
LICENSE.md
NOTICE.md
README.md
```

# Files

## File: .github/FUNDING.yml
```yaml
1: # These are supported funding model platforms
2: 
3: github: [ai-dock, robballantyne]
```

## File: .github/workflows/build-env.yml
```yaml
 1: name: Build Env
 2: 
 3: on:
 4:  workflow_dispatch:
 5: 
 6: env:
 7:   UBUNTU_VERSION: 22.04
 8:   BUILDX_NO_DEFAULT_ATTESTATIONS: 1
 9: 
10: jobs:
11:   cpu-base:
12:     runs-on: ubuntu-latest
13:     strategy:
14:       fail-fast: false
15:       matrix:
16:         build:
17:           # Undeclared SHA tags with latest commit from master branch
18:           - {latest: "false", python: "3.10", pytorch: "2.2.1"}
19:           - {latest: "true", sha: "abc1234", python: "3.10", pytorch: "2.2.1"}
20:     steps:
21:       -
22:         name: Env Setter
23:         run: |
24:           echo "PACKAGE_NAME=${GITHUB_REPOSITORY,,}" >> ${GITHUB_ENV}
25:       -
26:         name: Set tags
27:         run: |
28:           img_path="ghcr.io/${{ env.PACKAGE_NAME }}"
29:           if [[ -z '${{ matrix.build.sha }}' ]]; then
30:               COMFYUI_SHA="$(curl -fsSL "https://api.github.com/repos/comfyanonymous/ComfyUI/commits/master" | jq -r '.sha[0:7]')"
31:           else
32:               COMFYUI_SHA="${{ matrix.build.sha }}"
33:           fi
34:           [ -z "$COMFYUI_SHA" ] && { echo "Error: COMFYUI_SHA is empty. Exiting script." >&2; exit 1; }
35:           
36:           base_tag="newbase-${{ matrix.build.pytorch }}-py${{ matrix.build.python }}-cpu-${{ env.UBUNTU_VERSION }}"
37:           sha_tag="${base_tag}-${COMFYUI_SHA}"
38:           TAGS="${img_path}:${sha_tag}"
39:           if [[ ${{ matrix.build.latest }} == "true" ]]; then
40:               echo "Marking latest"
41:               TAGS+=", ${img_path}:latest-cpu, ${img_path}:latest-cpu-jupyter"
42:           fi
```

## File: .github/workflows/clear-cache.yml
```yaml
 1: # https://stackoverflow.com/a/73556714
 2: name: Clear Cache
 3: 
 4: on:
 5:   workflow_dispatch:
 6: 
 7: permissions:
 8:   actions: write
 9: 
10: jobs:
11:   clear-cache:
12:     runs-on: ubuntu-latest
13:     steps:
14:       - name: Clear cache
15:         uses: actions/github-script@v6
16:         with:
17:           script: |
18:             console.log("About to clear")
19:             const response = await github.rest.actions.getActionsCacheList({
20:                 owner: context.repo.owner,
21:                 repo: context.repo.repo,
22:                 page: 1,
23:                 per_page: 100
24:             });
25:             
26:             const pages = (function() { 
27:                 if (typeof response.headers.link !== 'undefined') {
28:                     return response.headers.link.split(">").slice(-2)[0].split('=').slice(-1)[0]
29:                 }
30:                 return 1;
31:             })();
32:             
33:             console.log("Total pages: " + pages);
34:             
35:             for (let page = pages; page >= 1; page--) {
36:                 console.log("Processing page " + page)
37:               
38:                 const response = await github.rest.actions.getActionsCacheList({
39:                     owner: context.repo.owner,
40:                     repo: context.repo.repo,
41:                     page: page,
42:                     per_page: 100
43:                 });
44:                 
45:                 for (const cache of response.data.actions_caches) {
46:                     console.log(cache)
47:                     github.rest.actions.deleteActionsCacheById({
48:                         owner: context.repo.owner,
49:                         repo: context.repo.repo,
50:                         cache_id: cache.id,
51:                     })
52:                 }
53:             }
54:             
55:             console.log("Clear completed")
```

## File: .github/workflows/delete-old-images.yml
```yaml
  1: name: Delete Old Packages
  2: 
  3: env:
  4:   PER_PAGE: 100
  5: 
  6: on:
  7:   workflow_dispatch:
  8:       inputs:
  9:           age:
 10:             type: choice
 11:             required: true
 12:             description: Delete older than
 13:             options: 
 14:             - 1 Hour
 15:             - 12 Hours
 16:             - 1 Day
 17:             - 1 Week
 18:             - 2 Weeks
 19:             - 1 Month
 20:             - 6 Months
 21:             - 1 Year
 22:             - 2 Years
 23:             - 3 Years
 24:             - 4 Years
 25:             - 5 Years
 26:             - All Packages
 27: 
 28: jobs:
 29:   delete-old-packages:
 30:     runs-on: ubuntu-latest
 31:     steps:
 32:       -
 33:         run: |
 34:           echo "PACKAGE_NAME=${GITHUB_REPOSITORY,,}" >> ${GITHUB_ENV}
 35:           echo "OWNER=orgs/${GITHUB_REPOSITORY_OWNER,,}" >> ${GITHUB_ENV}
 36:       -
 37:         uses: actions/github-script@v6
 38:         with:
 39:           github-token: ${{ secrets.DELETE_PACKAGES_TOKEN }}
 40:           script: |
 41:             const delete_age = (function() {
 42:                 switch ("${{ github.event.inputs.age }}") {
 43:                     case "All Packages":
 44:                         return 0;
 45:                     case "1 Hour":
 46:                         return 60;
 47:                     case "12 Hours":
 48:                         return 720;
 49:                     case "1 Day":
 50:                         return 1440;
 51:                     case "1 Week":
 52:                         return 10080;
 53:                     case "2 Weeks":
 54:                         return 20160;
 55:                     case "1 Month":
 56:                         return 43800;
 57:                     case "6 Months":
 58:                         return 262800;
 59:                     case "1 Year":
 60:                         return 525600;
 61:                     case "2 Years":
 62:                         return 525600 * 2;
 63:                     case "3 Years":
 64:                         return 525600 * 3;
 65:                     case "4 Years":
 66:                         return 525600 * 4;
 67:                     case "5 Years":
 68:                         return 525600 * 5;
 69:                     default:
 70:                         return 157680000;
 71:                 }
 72:             })();
 73:             
 74:             const now = new Date();
 75:             const epoch_minutes = Math.round(now.getTime() / 1000 / 60);
 76:             
 77:             const response = await github.request("GET /${{ env.OWNER }}/packages/container/${{ github.event.repository.name  }}/versions",
 78:               { per_page: ${{ env.PER_PAGE }}
 79:             });
 80: 
 81:             const pages = (function() { 
 82:                 if (typeof response.headers.link !== 'undefined') {
 83:                 return response.headers.link.split(">").slice(-2)[0].split('=').slice(-1)[0]
 84:                 }
 85:                 return 1;
 86:             })();
 87: 
 88:             console.log("Total pages: " + pages);
 89:             
 90:             for (let page = pages; page >= 1; page--) {
 91:               console.log("Processing page " + page)
 92:               
 93:               const response = await github.request("GET /${{ env.OWNER }}/packages/container/${{ github.event.repository.name  }}/versions",
 94:               { 
 95:                   per_page: ${{ env.PER_PAGE }},
 96:                   page: page
 97:               });
 98:               
 99:               console.log("Deleting packages updated more than " + delete_age + " minutes ago...")
100:               for (version of response.data) {
101:                 let updated_at = new Date(version.updated_at)
102:                 let minutes_old = epoch_minutes - Math.round(updated_at.getTime() / 1000 / 60);
103:                 console.log("Package is " + minutes_old + " minutes old")
104:                 if (minutes_old > delete_age) {
105:                     console.log("delete " + version.id)
106:                     const deleteResponse = await github.request("DELETE /${{ env.OWNER }}/packages/container/${{ github.event.repository.name }}/versions/" + version.id, { });
107:                         console.log("status " + deleteResponse.status)
108:                 }
109:               }
110:             }
```

## File: .github/workflows/delete-untagged-images.yml
```yaml
 1: name: Delete Untagged Packages
 2: 
 3: env:
 4:   PER_PAGE: 100
 5: 
 6: on:
 7:   workflow_dispatch:
 8:   workflow_run:
 9:     workflows: ["Docker Build"]
10:     types:
11:       - completed
12: 
13: jobs:
14:   delete-untagged:
15:     runs-on: ubuntu-latest
16:     steps:
17:       -
18:         run: |
19:           echo "PACKAGE_NAME=${GITHUB_REPOSITORY,,}" >> ${GITHUB_ENV}
20:           echo "OWNER=orgs/${GITHUB_REPOSITORY_OWNER,,}" >> ${GITHUB_ENV}
21:       -
22:         uses: actions/github-script@v6
23:         with:
24:           github-token: ${{ secrets.DELETE_PACKAGES_TOKEN }}
25:           script: |
26:             const response = await github.request("GET /${{ env.OWNER }}/packages/container/${{ github.event.repository.name  }}/versions",
27:               { per_page: ${{ env.PER_PAGE }}
28:             });
29: 
30:             const pages = (function() { 
31:                 if (typeof response.headers.link !== 'undefined') {
32:                 return response.headers.link.split(">").slice(-2)[0].split('=').slice(-1)[0]
33:                 }
34:                 return 1;
35:             })();
36: 
37:             console.log("Total pages: " + pages);
38:             
39:             for (let page = pages; page >= 1; page--) {
40:               console.log("Processing page " + page)
41:               
42:               const response = await github.request("GET /${{ env.OWNER }}/packages/container/${{ github.event.repository.name  }}/versions",
43:               { 
44:                   per_page: ${{ env.PER_PAGE }},
45:                   page: page
46:               });
47:               
48:               for (version of response.data) {
49:                 if (version.metadata.container.tags.length == 0) {
50:                     console.log("delete " + version.id)
51:                     const deleteResponse = await github.request("DELETE /${{ env.OWNER }}/packages/container/${{ github.event.repository.name }}/versions/" + version.id, { });
52:                         console.log("status " + deleteResponse.status)
53:                 }
54:               }
55:             }
```

## File: .github/workflows/docker-build.yml
```yaml
  1: name: Docker Build
  2: 
  3: on:
  4:   workflow_dispatch:
  5:   #push:
  6:   #  branches: [ "main" ]
  7:     
  8: env:
  9:   UBUNTU_VERSION: 22.04
 10:   BUILDX_NO_DEFAULT_ATTESTATIONS: 1
 11: 
 12: jobs:
 13:   cpu-base:
 14:     runs-on: ubuntu-latest
 15:     strategy:
 16:       fail-fast: false
 17:       matrix:
 18:         build:
 19:           - {latest: "false", comfyui: "v0.2.7", python: "3.10", pytorch: "2.5.1"}
 20:     steps:
 21:       -
 22:         name: Free Space
 23:         run: |
 24:           df -h
 25:           sudo rm -rf /usr/share/dotnet
 26:           sudo rm -rf /opt/ghc
 27:           sudo rm -rf /usr/local/.ghcup
 28:           sudo rm -rf /usr/local/share/boost
 29:           sudo rm -rf /usr/local/lib/android
 30:           sudo rm -rf "$AGENT_TOOLSDIRECTORY"
 31:           df -h
 32:       -
 33:         name: Env Setter
 34:         run: |
 35:           REPO=${GITHUB_REPOSITORY,,}
 36:           echo "REPO_NAMESPACE=${REPO%%/*}" >> ${GITHUB_ENV}
 37:           echo "REPO_NAME=${REPO#*/}" >> ${GITHUB_ENV}
 38:       -
 39:         name: Checkout
 40:         uses: actions/checkout@v3
 41:       -
 42:         name: Permissions fixes
 43:         run: |
 44:           target="${HOME}/work/${{ env.REPO_NAME }}/${{ env.REPO_NAME }}/build/COPY*"
 45:           chmod -R ug+rwX ${target}
 46:       -
 47:         name: Login to DockerHub
 48:         uses: docker/login-action@v3
 49:         with:
 50:           username: ${{ vars.DOCKERHUB_USER }}
 51:           password: ${{ secrets.DOCKERHUB_TOKEN }}
 52:       -
 53:         name: Login to GitHub Container Registry
 54:         uses: docker/login-action@v3
 55:         with:
 56:           registry: ghcr.io
 57:           username: ${{ github.actor }}
 58:           password: ${{ secrets.GITHUB_TOKEN }}
 59:       -
 60:         name: Set tags
 61:         run: |
 62:             img_path_ghcr="ghcr.io/${{ env.REPO_NAMESPACE }}/${{ env.REPO_NAME }}"
 63:             if [[ -z '${{ matrix.build.comfyui }}' ]]; then
 64:                 COMFYUI_BUILD_REF="$(curl -s https://api.github.com/repos/comfyanonymous/ComfyUI/tags | jq -r '.[0].name')"
 65:             else
 66:                 COMFYUI_BUILD_REF="${{ matrix.build.comfyui }}"
 67:             fi
 68:             [ -z "$COMFYUI_BUILD_REF" ] && { echo "Error: COMFYUI_BUILD_REF is empty. Exiting script." >&2; exit 1; }
 69:             echo "COMFYUI_BUILD_REF=${COMFYUI_BUILD_REF}" >> ${GITHUB_ENV}
 70: 
 71:             base_tag="v2-cpu-${{ env.UBUNTU_VERSION }}"
 72: 
 73:             if [[ ${{ matrix.build.latest }} == "true" ]]; then
 74:                 echo "Marking latest"
 75:                 TAGS="${img_path_ghcr}:${base_tag}-${COMFYUI_BUILD_REF}, ${img_path_ghcr}:${base_tag}, ${img_path_ghcr}:latest-cpu"
 76:             else
 77:                 TAGS="${img_path_ghcr}:${base_tag}-${COMFYUI_BUILD_REF}"
 78:             fi
 79:             echo "TAGS=${TAGS}" >> ${GITHUB_ENV}
 80:       -
 81:         name: Build and push
 82:         uses: docker/build-push-action@v4
 83:         with:
 84:           context: build
 85:           build-args: |
 86:             IMAGE_BASE=ghcr.io/ai-dock/python:${{ matrix.build.python }}-v2-cpu-${{ env.UBUNTU_VERSION }}
 87:             PYTHON_VERSION=${{ matrix.build.python }}
 88:             PYTORCH_VERSION=${{ matrix.build.pytorch }}
 89:             COMFYUI_BUILD_REF=${{ env.COMFYUI_BUILD_REF }}
 90:           push: true
 91:           # Avoids unknown/unknown architecture and extra metadata
 92:           provenance: false
 93:           tags: ${{ env.TAGS }}
 94:     
 95:   nvidia-base:
 96:     runs-on: ubuntu-latest
 97:     strategy:
 98:       fail-fast: false
 99:       matrix:
100:         build:
101:           - {latest: "false", comfyui: "v0.2.7", python: "3.10", pytorch: "2.5.1", cuda: "12.1.1-base"}
102:           - {latest: "false", comfyui: "v0.2.7", python: "3.10", pytorch: "2.5.1", cuda: "12.1.1-cudnn8-devel"}
103:     steps:
104:       -
105:         name: Free Space
106:         run: |
107:           df -h
108:           sudo rm -rf /usr/share/dotnet
109:           sudo rm -rf /opt/ghc
110:           sudo rm -rf /usr/local/.ghcup
111:           sudo rm -rf /usr/local/share/boost
112:           sudo rm -rf /usr/local/lib/android
113:           sudo rm -rf "$AGENT_TOOLSDIRECTORY"
114:           df -h
115:       -
116:         name: Env Setter
117:         run: |
118:           REPO=${GITHUB_REPOSITORY,,}
119:           echo "REPO_NAMESPACE=${REPO%%/*}" >> ${GITHUB_ENV}
120:           echo "REPO_NAME=${REPO#*/}" >> ${GITHUB_ENV}
121:       -
122:         name: Checkout
123:         uses: actions/checkout@v3
124:       -
125:         name: Permissions fixes
126:         run: |
127:           target="${HOME}/work/${{ env.REPO_NAME }}/${{ env.REPO_NAME }}/build/COPY*"
128:           chmod -R ug+rwX ${target}
129:       -
130:         name: Login to DockerHub
131:         uses: docker/login-action@v3
132:         with:
133:           username: ${{ vars.DOCKERHUB_USER }}
134:           password: ${{ secrets.DOCKERHUB_TOKEN }}
135:       -
136:         name: Login to GitHub Container Registry
137:         uses: docker/login-action@v3
138:         with:
139:           registry: ghcr.io
140:           username: ${{ github.actor }}
141:           password: ${{ secrets.GITHUB_TOKEN }}
142:       -
143:         name: Set tags
144:         run: |
145:           img_path_ghcr="ghcr.io/${{ env.REPO_NAMESPACE }}/${{ env.REPO_NAME }}"
146:           img_path_dhub="${{ vars.DOCKERHUB_USER }}/${{ env.REPO_NAME }}-cuda"
147:           if [[ -z '${{ matrix.build.comfyui }}' ]]; then
148:               COMFYUI_BUILD_REF="$(curl -s https://api.github.com/repos/comfyanonymous/ComfyUI/tags | jq -r '.[0].name')"
149:           else
150:               COMFYUI_BUILD_REF="${{ matrix.build.comfyui }}"
151:           fi
152:           [ -z "$COMFYUI_BUILD_REF" ] && { echo "Error: COMFYUI_BUILD_REF is empty. Exiting script." >&2; exit 1; }
153:           echo "COMFYUI_BUILD_REF=${COMFYUI_BUILD_REF}" >> ${GITHUB_ENV}
154: 
155:           base_tag="v2-cuda-${{ matrix.build.cuda }}-${{ env.UBUNTU_VERSION }}"
156: 
157:           if [[ ${{ matrix.build.latest }} == "true" ]]; then
158:                 echo "Marking latest"
159:                 # GHCR.io Tags
160:                 TAGS="${img_path_ghcr}:${base_tag}-${COMFYUI_BUILD_REF}, ${img_path_ghcr}:${base_tag}, ${img_path_ghcr}:latest, ${img_path_ghcr}:latest-cuda"
161:                 # Docker.io Tags
162:                 TAGS="${TAGS}, ${img_path_dhub}:${COMFYUI_BUILD_REF}, ${img_path_dhub}:latest"
163:             else
164:                 TAGS="${img_path_ghcr}:${base_tag}-${COMFYUI_BUILD_REF}, ${img_path_dhub}:${COMFYUI_BUILD_REF}"
165:             fi
166:             # Tag a devel build
167:             if [[ ${{ matrix.build.cuda }} = *-devel ]]; then
168:                 TAGS="${TAGS}, ${img_path_dhub}:${COMFYUI_BUILD_REF}-devel"
169:             fi
170:           echo "TAGS=${TAGS}" >> ${GITHUB_ENV}
171:       -
172:         name: Build and push
173:         uses: docker/build-push-action@v4
174:         with:
175:           context: build
176:           build-args: |
177:             IMAGE_BASE=ghcr.io/ai-dock/python:${{ matrix.build.python }}-v2-cuda-${{ matrix.build.cuda }}-${{ env.UBUNTU_VERSION }}
178:             PYTHON_VERSION=${{ matrix.build.python }}
179:             PYTORCH_VERSION=${{ matrix.build.pytorch }}
180:             COMFYUI_BUILD_REF=${{ env.COMFYUI_BUILD_REF }}
181:           push: true
182:           provenance: false
183:           tags: ${{ env.TAGS }}
184: 
185:   amd-base:
186:     runs-on: ubuntu-latest
187:     strategy:
188:       fail-fast: false
189:       matrix:
190:         build:
191:           - {latest: "false", comfyui: "v0.2.7", python: "3.10", pytorch: "2.3.1", rocm: "6.0-runtime"}
192:     steps:
193:       -
194:         name: Free Space
195:         run: |
196:           df -h
197:           sudo rm -rf /usr/share/dotnet
198:           sudo rm -rf /opt/ghc
199:           sudo rm -rf /usr/local/.ghcup
200:           sudo rm -rf /usr/local/share/boost
201:           sudo rm -rf /usr/local/lib/android
202:           sudo rm -rf "$AGENT_TOOLSDIRECTORY"
203:           df -h
204:       -
205:         name: Env Setter
206:         run: |
207:           REPO=${GITHUB_REPOSITORY,,}
208:           echo "REPO_NAMESPACE=${REPO%%/*}" >> ${GITHUB_ENV}
209:           echo "REPO_NAME=${REPO#*/}" >> ${GITHUB_ENV}
210:       -
211:         name: Checkout
212:         uses: actions/checkout@v3
213:       -
214:         name: Permissions fixes
215:         run: |
216:           target="${HOME}/work/${{ env.REPO_NAME }}/${{ env.REPO_NAME }}/build/COPY*"
217:           chmod -R ug+rwX ${target}
218:       -
219:         name: Login to DockerHub
220:         uses: docker/login-action@v3
221:         with:
222:           username: ${{ vars.DOCKERHUB_USER }}
223:           password: ${{ secrets.DOCKERHUB_TOKEN }}
224:       -
225:         name: Login to GitHub Container Registry
226:         uses: docker/login-action@v3
227:         with:
228:           registry: ghcr.io
229:           username: ${{ github.actor }}
230:           password: ${{ secrets.GITHUB_TOKEN }}
231:       -
232:         name: Set tags
233:         run: |
234:             img_path_ghcr="ghcr.io/${{ env.REPO_NAMESPACE }}/${{ env.REPO_NAME }}"
235:             img_path_dhub="${{ vars.DOCKERHUB_USER }}/${{ env.REPO_NAME }}-rocm"
236:             if [[ -z '${{ matrix.build.comfyui }}' ]]; then
237:                 COMFYUI_BUILD_REF="$(curl -s https://api.github.com/repos/comfyanonymous/ComfyUI/tags | jq -r '.[0].name')"
238:             else
239:                 COMFYUI_BUILD_REF="${{ matrix.build.comfyui }}"
240:             fi
241:             [ -z "$COMFYUI_BUILD_REF" ] && { echo "Error: COMFYUI_BUILD_REF is empty. Exiting script." >&2; exit 1; }
242:             echo "COMFYUI_BUILD_REF=${COMFYUI_BUILD_REF}" >> ${GITHUB_ENV}
243: 
244:             base_tag="v2-rocm-${{ matrix.build.rocm }}-${{ env.UBUNTU_VERSION }}"
245: 
246:             if [[ ${{ matrix.build.latest }} == "true" ]]; then
247:                 echo "Marking latest"
248:                 # GHCR.io Tags
249:                 TAGS="${img_path_ghcr}:${base_tag}-${COMFYUI_BUILD_REF}, ${img_path_ghcr}:${base_tag}, ${img_path_ghcr}:latest-rocm"
250:                 # Docker.io Tags
251:                 TAGS="${TAGS}, ${img_path_dhub}:${COMFYUI_BUILD_REF}, ${img_path_dhub}:latest"
252:             else
253:                 TAGS="${img_path_ghcr}:${base_tag}-${COMFYUI_BUILD_REF}, ${img_path_dhub}:${COMFYUI_BUILD_REF}"
254:             fi
255:             echo "TAGS=${TAGS}" >> ${GITHUB_ENV}
256:       -
257:         name: Build and push
258:         uses: docker/build-push-action@v4
259:         with:
260:           context: build
261:           build-args: |
262:             IMAGE_BASE=ghcr.io/ai-dock/python:${{ matrix.build.python }}-v2-rocm-${{ matrix.build.rocm }}-${{ env.UBUNTU_VERSION }}
263:             PYTHON_VERSION=${{ matrix.build.python }}
264:             PYTORCH_VERSION=${{ matrix.build.pytorch }}
265:             COMFYUI_BUILD_REF=${{ env.COMFYUI_BUILD_REF }}
266:           push: true
267:           provenance: false
268:           tags: ${{ env.TAGS }}
```

## File: .gitignore
```
1: workspace
2: *__pycache__
3: build/COPY_ROOT_EXTRA/
4: config/authorized_keys
5: config/rclone
6: tpdocs/
7: .env
```

## File: config/provisioning/animated.sh
```bash
 1: #!/bin/bash
 2: 
 3: # This file will be sourced in init.sh
 4: 
 5: # https://raw.githubusercontent.com/ai-dock/comfyui/main/config/provisioning/animated.sh
 6: printf "\n##############################################\n#                                            #\n#          Provisioning container            #\n#                                            #\n#         This will take some time           #\n#                                            #\n# Your container will be ready on completion #\n#                                            #\n##############################################\n\n"
 7: function download() {
 8:     wget -q --show-progress -e dotbytes="${3:-4M}" -O "$2" "$1"
 9: }
10: 
11: ## Set paths
12: nodes_dir=/opt/ComfyUI/custom_nodes
13: models_dir=/opt/ComfyUI/models
14: checkpoints_dir=${models_dir}/checkpoints
15: vae_dir=${models_dir}/vae
16: controlnet_dir=${models_dir}/controlnet
17: loras_dir=${models_dir}/loras
18: upscale_dir=${models_dir}/upscale_models
19: 
20: ### Install custom nodes
21: 
22: # ComfyUI-Manager
23: this_node_dir=${nodes_dir}/ComfyUI-Manager
24: if [[ ! -d $this_node_dir ]]; then
25:     git clone https://github.com/ltdrdata/ComfyUI-Manager $this_node_dir
26: else
27:     (cd $this_node_dir && git pull)
28: fi
29: 
30: # ComfyUI-AnimateDiff-Evolved
31: this_node_dir=${nodes_dir}/ComfyUI-AnimateDiff-Evolved
32: if [[ ! -d $this_node_dir ]]; then
33:     git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved $this_node_dir
34: else
35:     (cd $this_node_dir && git pull)
36: fi
37: 
38: animated_models_dir=${nodes_dir}/ComfyUI-AnimateDiff-Evolved/models
39: 
40: # ComfyUI-Advanced-ControlNet
41: this_node_dir=${nodes_dir}/ComfyUI-Advanced-ControlNet
42: if [[ ! -d $this_node_dir ]]; then
43:     git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet $this_node_dir
44: else
45:     (cd $this_node_dir && git pull)
46: fi
47: 
48: ### Download checkpoints
49: 
50: ## Animated
51: # mm_sd_v15
52: model_file=${animated_models_dir}/mm_sd_v15.ckpt
53: model_url=https://huggingface.co/guoyww/animatediff/resolve/main/mm_sd_v15.ckpt
54: if [[ ! -e ${model_file} ]]; then
55:     printf "mm_sd_v15.ckpt...\n"
56:     download ${model_url} ${model_file}
57: fi
58: 
59: ## Standard
60: # v1-5-pruned-emaonly
61: model_file=${checkpoints_dir}/v1-5-pruned-emaonly.ckpt
62: model_url=https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.ckpt
63: 
64: if [[ ! -e ${model_file} ]]; then
65:     printf "Downloading Stable Diffusion 1.5...\n"
66:     download ${model_url} ${model_file}
67: fi
68: 
69: ### Download controlnet
70: 
71: ## example
72: 
73: #model_file=${controlnet_dir}/control_canny-fp16.safetensors
74: #model_url=https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_canny-fp16.safetensors
75: 
76: #if [[ ! -e ${model_file} ]]; then
77: #    printf "Downloading Canny...\n"
78: #    download ${model_url} ${model_file}
79: #fi
80: 
81: ### Download loras
82: 
83: ## example
84: 
85: #model_file=${loras_dir}/epi_noiseoffset2.safetensors
86: #model_url=https://civitai.com/api/download/models/16576
87: 
88: #if [[ ! -e ${model_file} ]]; then
89: #    printf "Downloading epi_noiseoffset2 lora...\n"
90: #    download ${model_url} ${model_file}
91: #fi
```

## File: config/provisioning/default.sh
```bash
  1: #!/bin/bash
  2: 
  3: # This file will be sourced in init.sh
  4: 
  5: # https://raw.githubusercontent.com/ai-dock/comfyui/main/config/provisioning/default.sh
  6: 
  7: # Packages are installed after nodes so we can fix them...
  8: 
  9: #DEFAULT_WORKFLOW="https://..."
 10: 
 11: APT_PACKAGES=(
 12:     #"package-1"
 13:     #"package-2"
 14: )
 15: 
 16: PIP_PACKAGES=(
 17:     #"package-1"
 18:     #"package-2"
 19: )
 20: 
 21: NODES=(
 22:     "https://github.com/ltdrdata/ComfyUI-Manager"
 23:     "https://github.com/cubiq/ComfyUI_essentials"
 24: )
 25: 
 26: CHECKPOINT_MODELS=(
 27:     "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.ckpt"
 28:     #"https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.ckpt"
 29:     "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors"
 30:     "https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors"
 31: )
 32: 
 33: UNET_MODELS=(
 34: 
 35: )
 36: 
 37: LORA_MODELS=(
 38:     #"https://civitai.com/api/download/models/16576"
 39: )
 40: 
 41: VAE_MODELS=(
 42:     "https://huggingface.co/stabilityai/sd-vae-ft-ema-original/resolve/main/vae-ft-ema-560000-ema-pruned.safetensors"
 43:     "https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors"
 44:     "https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors"
 45: )
 46: 
 47: ESRGAN_MODELS=(
 48:     "https://huggingface.co/ai-forever/Real-ESRGAN/resolve/main/RealESRGAN_x4.pth"
 49:     "https://huggingface.co/FacehugmanIII/4x_foolhardy_Remacri/resolve/main/4x_foolhardy_Remacri.pth"
 50:     "https://huggingface.co/Akumetsu971/SD_Anime_Futuristic_Armor/resolve/main/4x_NMKD-Siax_200k.pth"
 51: )
 52: 
 53: CONTROLNET_MODELS=(
 54:     "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/diffusers_xl_canny_mid.safetensors"
 55:     "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/diffusers_xl_depth_mid.safetensors?download"
 56:     "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/t2i-adapter_diffusers_xl_openpose.safetensors"
 57:     "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_canny-fp16.safetensors"
 58:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_depth-fp16.safetensors"
 59:     "https://huggingface.co/kohya-ss/ControlNet-diff-modules/resolve/main/diff_control_sd15_depth_fp16.safetensors"
 60:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_hed-fp16.safetensors"
 61:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_mlsd-fp16.safetensors"
 62:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_normal-fp16.safetensors"
 63:     "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_openpose-fp16.safetensors"
 64:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_scribble-fp16.safetensors"
 65:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_seg-fp16.safetensors"
 66:     "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_canny-fp16.safetensors"
 67:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_color-fp16.safetensors"
 68:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_depth-fp16.safetensors"
 69:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_keypose-fp16.safetensors"
 70:     "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_openpose-fp16.safetensors"
 71:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_seg-fp16.safetensors"
 72:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_sketch-fp16.safetensors"
 73:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_style-fp16.safetensors"
 74: )
 75: 
 76: ### DO NOT EDIT BELOW HERE UNLESS YOU KNOW WHAT YOU ARE DOING ###
 77: 
 78: function provisioning_start() {
 79:     if [[ ! -d /opt/environments/python ]]; then 
 80:         export MAMBA_BASE=true
 81:     fi
 82:     source /opt/ai-dock/etc/environment.sh
 83:     source /opt/ai-dock/bin/venv-set.sh comfyui
 84: 
 85:     provisioning_print_header
 86:     provisioning_get_apt_packages
 87:     provisioning_get_nodes
 88:     provisioning_get_pip_packages
 89:     provisioning_get_models \
 90:         "${WORKSPACE}/storage/stable_diffusion/models/ckpt" \
 91:         "${CHECKPOINT_MODELS[@]}"
 92:     provisioning_get_models \
 93:         "${WORKSPACE}/storage/stable_diffusion/models/unet" \
 94:         "${UNET_MODELS[@]}"
 95:     provisioning_get_models \
 96:         "${WORKSPACE}/storage/stable_diffusion/models/lora" \
 97:         "${LORA_MODELS[@]}"
 98:     provisioning_get_models \
 99:         "${WORKSPACE}/storage/stable_diffusion/models/controlnet" \
100:         "${CONTROLNET_MODELS[@]}"
101:     provisioning_get_models \
102:         "${WORKSPACE}/storage/stable_diffusion/models/vae" \
103:         "${VAE_MODELS[@]}"
104:     provisioning_get_models \
105:         "${WORKSPACE}/storage/stable_diffusion/models/esrgan" \
106:         "${ESRGAN_MODELS[@]}"
107:     provisioning_print_end
108: }
109: 
110: function pip_install() {
111:     if [[ -z $MAMBA_BASE ]]; then
112:             "$COMFYUI_VENV_PIP" install --no-cache-dir "$@"
113:         else
114:             micromamba run -n comfyui pip install --no-cache-dir "$@"
115:         fi
116: }
117: 
118: function provisioning_get_apt_packages() {
119:     if [[ -n $APT_PACKAGES ]]; then
120:             sudo $APT_INSTALL ${APT_PACKAGES[@]}
121:     fi
122: }
123: 
124: function provisioning_get_pip_packages() {
125:     if [[ -n $PIP_PACKAGES ]]; then
126:             pip_install ${PIP_PACKAGES[@]}
127:     fi
128: }
129: 
130: function provisioning_get_nodes() {
131:     for repo in "${NODES[@]}"; do
132:         dir="${repo##*/}"
133:         path="/opt/ComfyUI/custom_nodes/${dir}"
134:         requirements="${path}/requirements.txt"
135:         if [[ -d $path ]]; then
136:             if [[ ${AUTO_UPDATE,,} != "false" ]]; then
137:                 printf "Updating node: %s...\n" "${repo}"
138:                 ( cd "$path" && git pull )
139:                 if [[ -e $requirements ]]; then
140:                    pip_install -r "$requirements"
141:                 fi
142:             fi
143:         else
144:             printf "Downloading node: %s...\n" "${repo}"
145:             git clone "${repo}" "${path}" --recursive
146:             if [[ -e $requirements ]]; then
147:                 pip_install -r "${requirements}"
148:             fi
149:         fi
150:     done
151: }
152: 
153: function provisioning_get_default_workflow() {
154:     if [[ -n $DEFAULT_WORKFLOW ]]; then
155:         workflow_json=$(curl -s "$DEFAULT_WORKFLOW")
156:         if [[ -n $workflow_json ]]; then
157:             echo "export const defaultGraph = $workflow_json;" > /opt/ComfyUI/web/scripts/defaultGraph.js
158:         fi
159:     fi
160: }
161: 
162: function provisioning_get_models() {
163:     if [[ -z $2 ]]; then return 1; fi
164:     
165:     dir="$1"
166:     mkdir -p "$dir"
167:     shift
168:     arr=("$@")
169:     printf "Downloading %s model(s) to %s...\n" "${#arr[@]}" "$dir"
170:     for url in "${arr[@]}"; do
171:         printf "Downloading: %s\n" "${url}"
172:         provisioning_download "${url}" "${dir}"
173:         printf "\n"
174:     done
175: }
176: 
177: function provisioning_print_header() {
178:     printf "\n##############################################\n#                                            #\n#          Provisioning container            #\n#                                            #\n#         This will take some time           #\n#                                            #\n# Your container will be ready on completion #\n#                                            #\n##############################################\n\n"
179:     if [[ $DISK_GB_ALLOCATED -lt $DISK_GB_REQUIRED ]]; then
180:         printf "WARNING: Your allocated disk size (%sGB) is below the recommended %sGB - Some models will not be downloaded\n" "$DISK_GB_ALLOCATED" "$DISK_GB_REQUIRED"
181:     fi
182: }
183: 
184: function provisioning_print_end() {
185:     printf "\nProvisioning complete:  Web UI will start now\n\n"
186: }
187: 
188: function provisioning_has_valid_hf_token() {
189:     [[ -n "$HF_TOKEN" ]] || return 1
190:     url="https://huggingface.co/api/whoami-v2"
191: 
192:     response=$(curl -o /dev/null -s -w "%{http_code}" -X GET "$url" \
193:         -H "Authorization: Bearer $HF_TOKEN" \
194:         -H "Content-Type: application/json")
195: 
196:     # Check if the token is valid
197:     if [ "$response" -eq 200 ]; then
198:         return 0
199:     else
200:         return 1
201:     fi
202: }
203: 
204: function provisioning_has_valid_civitai_token() {
205:     [[ -n "$CIVITAI_TOKEN" ]] || return 1
206:     url="https://civitai.com/api/v1/models?hidden=1&limit=1"
207: 
208:     response=$(curl -o /dev/null -s -w "%{http_code}" -X GET "$url" \
209:         -H "Authorization: Bearer $CIVITAI_TOKEN" \
210:         -H "Content-Type: application/json")
211: 
212:     # Check if the token is valid
213:     if [ "$response" -eq 200 ]; then
214:         return 0
215:     else
216:         return 1
217:     fi
218: }
219: 
220: # Download from $1 URL to $2 file path
221: function provisioning_download() {
222:     if [[ -n $HF_TOKEN && $1 =~ ^https://([a-zA-Z0-9_-]+\.)?huggingface\.co(/|$|\?) ]]; then
223:         auth_token="$HF_TOKEN"
224:     elif 
225:         [[ -n $CIVITAI_TOKEN && $1 =~ ^https://([a-zA-Z0-9_-]+\.)?civitai\.com(/|$|\?) ]]; then
226:         auth_token="$CIVITAI_TOKEN"
227:     fi
228:     if [[ -n $auth_token ]];then
229:         wget --header="Authorization: Bearer $auth_token" -qnc --content-disposition --show-progress -e dotbytes="${3:-4M}" -P "$2" "$1"
230:     else
231:         wget -qnc --content-disposition --show-progress -e dotbytes="${3:-4M}" -P "$2" "$1"
232:     fi
233: }
234: 
235: provisioning_start
```

## File: config/provisioning/flux.sh
```bash
  1: #!/bin/bash
  2: 
  3: # This file will be sourced in init.sh
  4: 
  5: # https://raw.githubusercontent.com/ai-dock/comfyui/main/config/provisioning/default.sh
  6: 
  7: # Packages are installed after nodes so we can fix them...
  8: 
  9: DEFAULT_WORKFLOW="https://raw.githubusercontent.com/ai-dock/comfyui/main/config/workflows/flux-comfyui-example.json"
 10: 
 11: APT_PACKAGES=(
 12:     #"package-1"
 13:     #"package-2"
 14: )
 15: 
 16: PIP_PACKAGES=(
 17:     #"package-1"
 18:     #"package-2"
 19: )
 20: 
 21: NODES=(
 22:     
 23: )
 24: 
 25: CHECKPOINT_MODELS=(
 26: )
 27: 
 28: CLIP_MODELS=(
 29:     "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors"
 30:     "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors"
 31: )
 32: 
 33: UNET_MODELS=(
 34: )
 35: 
 36: VAE_MODELS=(
 37: )
 38: 
 39: LORA_MODELS=(
 40: )
 41: 
 42: ESRGAN_MODELS=(
 43:     "https://huggingface.co/ai-forever/Real-ESRGAN/resolve/main/RealESRGAN_x4.pth"
 44:     "https://huggingface.co/FacehugmanIII/4x_foolhardy_Remacri/resolve/main/4x_foolhardy_Remacri.pth"
 45:     "https://huggingface.co/Akumetsu971/SD_Anime_Futuristic_Armor/resolve/main/4x_NMKD-Siax_200k.pth"
 46: )
 47: 
 48: CONTROLNET_MODELS=(
 49: )
 50: 
 51: ### DO NOT EDIT BELOW HERE UNLESS YOU KNOW WHAT YOU ARE DOING ###
 52: 
 53: function provisioning_start() {
 54:     if [[ ! -d /opt/environments/python ]]; then 
 55:         export MAMBA_BASE=true
 56:     fi
 57:     source /opt/ai-dock/etc/environment.sh
 58:     source /opt/ai-dock/bin/venv-set.sh comfyui
 59: 
 60:     # Get licensed models if HF_TOKEN set & valid
 61:     if provisioning_has_valid_hf_token; then
 62:         UNET_MODELS+=("https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors")
 63:         VAE_MODELS+=("https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors")
 64:     else
 65:         UNET_MODELS+=("https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/flux1-schnell.safetensors")
 66:         VAE_MODELS+=("https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors")
 67:         sed -i 's/flux1-dev\.safetensors/flux1-schnell.safetensors/g' /opt/ComfyUI/web/scripts/defaultGraph.js
 68:     fi
 69: 
 70:     provisioning_print_header
 71:     provisioning_get_apt_packages
 72:     provisioning_get_default_workflow
 73:     provisioning_get_nodes
 74:     provisioning_get_pip_packages
 75:     provisioning_get_models \
 76:         "${WORKSPACE}/storage/stable_diffusion/models/ckpt" \
 77:         "${CHECKPOINT_MODELS[@]}"
 78:     provisioning_get_models \
 79:         "${WORKSPACE}/storage/stable_diffusion/models/unet" \
 80:         "${UNET_MODELS[@]}"
 81:     provisioning_get_models \
 82:         "${WORKSPACE}/storage/stable_diffusion/models/lora" \
 83:         "${LORA_MODELS[@]}"
 84:     provisioning_get_models \
 85:         "${WORKSPACE}/storage/stable_diffusion/models/controlnet" \
 86:         "${CONTROLNET_MODELS[@]}"
 87:     provisioning_get_models \
 88:         "${WORKSPACE}/storage/stable_diffusion/models/vae" \
 89:         "${VAE_MODELS[@]}"
 90:     provisioning_get_models \
 91:         "${WORKSPACE}/storage/stable_diffusion/models/clip" \
 92:         "${CLIP_MODELS[@]}"
 93:     provisioning_get_models \
 94:         "${WORKSPACE}/storage/stable_diffusion/models/esrgan" \
 95:         "${ESRGAN_MODELS[@]}"
 96:     provisioning_print_end
 97: }
 98: 
 99: function pip_install() {
100:     if [[ -z $MAMBA_BASE ]]; then
101:             "$COMFYUI_VENV_PIP" install --no-cache-dir "$@"
102:         else
103:             micromamba run -n comfyui pip install --no-cache-dir "$@"
104:         fi
105: }
106: 
107: function provisioning_get_apt_packages() {
108:     if [[ -n $APT_PACKAGES ]]; then
109:             sudo $APT_INSTALL ${APT_PACKAGES[@]}
110:     fi
111: }
112: 
113: function provisioning_get_pip_packages() {
114:     if [[ -n $PIP_PACKAGES ]]; then
115:             pip_install ${PIP_PACKAGES[@]}
116:     fi
117: }
118: 
119: function provisioning_get_nodes() {
120:     for repo in "${NODES[@]}"; do
121:         dir="${repo##*/}"
122:         path="/opt/ComfyUI/custom_nodes/${dir}"
123:         requirements="${path}/requirements.txt"
124:         if [[ -d $path ]]; then
125:             if [[ ${AUTO_UPDATE,,} != "false" ]]; then
126:                 printf "Updating node: %s...\n" "${repo}"
127:                 ( cd "$path" && git pull )
128:                 if [[ -e $requirements ]]; then
129:                    pip_install -r "$requirements"
130:                 fi
131:             fi
132:         else
133:             printf "Downloading node: %s...\n" "${repo}"
134:             git clone "${repo}" "${path}" --recursive
135:             if [[ -e $requirements ]]; then
136:                 pip_install -r "${requirements}"
137:             fi
138:         fi
139:     done
140: }
141: 
142: function provisioning_get_default_workflow() {
143:     if [[ -n $DEFAULT_WORKFLOW ]]; then
144:         workflow_json=$(curl -s "$DEFAULT_WORKFLOW")
145:         if [[ -n $workflow_json ]]; then
146:             echo "export const defaultGraph = $workflow_json;" > /opt/ComfyUI/web/scripts/defaultGraph.js
147:         fi
148:     fi
149: }
150: 
151: function provisioning_get_models() {
152:     if [[ -z $2 ]]; then return 1; fi
153:     
154:     dir="$1"
155:     mkdir -p "$dir"
156:     shift
157:     arr=("$@")
158:     printf "Downloading %s model(s) to %s...\n" "${#arr[@]}" "$dir"
159:     for url in "${arr[@]}"; do
160:         printf "Downloading: %s\n" "${url}"
161:         provisioning_download "${url}" "${dir}"
162:         printf "\n"
163:     done
164: }
165: 
166: function provisioning_print_header() {
167:     printf "\n##############################################\n#                                            #\n#          Provisioning container            #\n#                                            #\n#         This will take some time           #\n#                                            #\n# Your container will be ready on completion #\n#                                            #\n##############################################\n\n"
168:     if [[ $DISK_GB_ALLOCATED -lt $DISK_GB_REQUIRED ]]; then
169:         printf "WARNING: Your allocated disk size (%sGB) is below the recommended %sGB - Some models will not be downloaded\n" "$DISK_GB_ALLOCATED" "$DISK_GB_REQUIRED"
170:     fi
171: }
172: 
173: function provisioning_print_end() {
174:     printf "\nProvisioning complete:  Web UI will start now\n\n"
175: }
176: 
177: function provisioning_has_valid_hf_token() {
178:     [[ -n "$HF_TOKEN" ]] || return 1
179:     url="https://huggingface.co/api/whoami-v2"
180: 
181:     response=$(curl -o /dev/null -s -w "%{http_code}" -X GET "$url" \
182:         -H "Authorization: Bearer $HF_TOKEN" \
183:         -H "Content-Type: application/json")
184: 
185:     # Check if the token is valid
186:     if [ "$response" -eq 200 ]; then
187:         return 0
188:     else
189:         return 1
190:     fi
191: }
192: 
193: function provisioning_has_valid_civitai_token() {
194:     [[ -n "$CIVITAI_TOKEN" ]] || return 1
195:     url="https://civitai.com/api/v1/models?hidden=1&limit=1"
196: 
197:     response=$(curl -o /dev/null -s -w "%{http_code}" -X GET "$url" \
198:         -H "Authorization: Bearer $CIVITAI_TOKEN" \
199:         -H "Content-Type: application/json")
200: 
201:     # Check if the token is valid
202:     if [ "$response" -eq 200 ]; then
203:         return 0
204:     else
205:         return 1
206:     fi
207: }
208: 
209: # Download from $1 URL to $2 file path
210: function provisioning_download() {
211:     if [[ -n $HF_TOKEN && $1 =~ ^https://([a-zA-Z0-9_-]+\.)?huggingface\.co(/|$|\?) ]]; then
212:         auth_token="$HF_TOKEN"
213:     elif 
214:         [[ -n $CIVITAI_TOKEN && $1 =~ ^https://([a-zA-Z0-9_-]+\.)?civitai\.com(/|$|\?) ]]; then
215:         auth_token="$CIVITAI_TOKEN"
216:     fi
217:     if [[ -n $auth_token ]];then
218:         wget --header="Authorization: Bearer $auth_token" -qnc --content-disposition --show-progress -e dotbytes="${3:-4M}" -P "$2" "$1"
219:     else
220:         wget -qnc --content-disposition --show-progress -e dotbytes="${3:-4M}" -P "$2" "$1"
221:     fi
222: }
223: 
224: provisioning_start
```

## File: config/provisioning/get-models-sd-official.sh
```bash
 1: #!/bin/bash
 2: 
 3: # This file will be sourced in init.sh
 4: 
 5: # https://raw.githubusercontent.com/ai-dock/comfyui/main/config/provisioning/get-models-sd-official.sh
 6: printf "\n##############################################\n#                                            #\n#          Provisioning container            #\n#                                            #\n#         This will take some time           #\n#                                            #\n# Your container will be ready on completion #\n#                                            #\n##############################################\n\n"
 7: function download() {
 8:     wget -q --show-progress -e dotbytes="${3:-4M}" -O "$2" "$1"
 9: }
10: # Download Stable Diffusion official models
11: 
12: models_dir=/opt/ComfyUI/models
13: checkpoints_dir=${models_dir}/checkpoints
14: vae_dir=${models_dir}/vae
15: loras_dir=${models_dir}/loras
16: upscale_dir=${models_dir}/upscale_models
17: 
18: # v1-5-pruned-emaonly
19: model_file=${checkpoints_dir}/v1-5-pruned-emaonly.ckpt
20: model_url=https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.ckpt
21: 
22: if [[ ! -e ${model_file} ]]; then
23:     printf "Downloading Stable Diffusion 1.5...\n"
24:     download ${model_url} ${model_file}
25: fi
26: 
27: # v2-1_768-ema-pruned
28: model_file=${checkpoints_dir}/v2-1_768-ema-pruned.ckpt
29: model_url=https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.ckpt
30: 
31: if [[ ! -e ${model_file} ]]; then
32:     printf "Downloading Stable Diffusion 2.1...\n"
33:     download ${model_url} ${model_file}
34: fi
35: 
36: # sd_xl_base_1
37: model_file=${checkpoints_dir}/sd_xl_base_1.0.safetensors
38: model_url=https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
39: 
40: if [[ ! -e ${model_file} ]]; then
41:     printf "Downloading Stable Diffusion XL base...\n"
42:     download ${model_url} ${model_file}
43: fi
44: 
45: # sd_xl_refiner_1
46: model_file=${checkpoints_dir}/sd_xl_refiner_1.0.safetensors
47: model_url=https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors
48: 
49: if [[ ! -e ${model_file} ]]; then
50:     printf "Downloading Stable Diffusion XL refiner...\n"
51:     download ${model_url} ${model_file}
52: fi
```

## File: config/provisioning/sd3.sh
```bash
  1: #!/bin/bash
  2: 
  3: # This file will be sourced in init.sh
  4: 
  5: # https://raw.githubusercontent.com/ai-dock/comfyui/main/config/provisioning/sd3.sh
  6: 
  7: # Packages are installed after nodes so we can fix them...
  8: 
  9: if [ -z "${HF_TOKEN}" ]; then
 10:     echo "HF_TOKEN is not set. Exiting."
 11:     exit 1
 12: fi
 13: 
 14: PYTHON_PACKAGES=(
 15:     #"opencv-python==4.7.0.72"
 16: )
 17: 
 18: NODES=(
 19:     "https://github.com/ltdrdata/ComfyUI-Manager"
 20: )
 21: 
 22: CHECKPOINT_MODELS=(
 23:     "https://huggingface.co/stabilityai/stable-diffusion-3-medium/resolve/main/sd3_medium_incl_clips_t5xxlfp16.safetensors"
 24: )
 25: 
 26: LORA_MODELS=(
 27:     #"https://civitai.com/api/download/models/16576"
 28: )
 29: 
 30: VAE_MODELS=(
 31:     "https://huggingface.co/stabilityai/sd-vae-ft-ema-original/resolve/main/vae-ft-ema-560000-ema-pruned.safetensors"
 32:     "https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors"
 33:     "https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors"
 34: )
 35: 
 36: ESRGAN_MODELS=(
 37:     "https://huggingface.co/ai-forever/Real-ESRGAN/resolve/main/RealESRGAN_x4.pth"
 38:     "https://huggingface.co/FacehugmanIII/4x_foolhardy_Remacri/resolve/main/4x_foolhardy_Remacri.pth"
 39:     "https://huggingface.co/Akumetsu971/SD_Anime_Futuristic_Armor/resolve/main/4x_NMKD-Siax_200k.pth"
 40: )
 41: 
 42: CONTROLNET_MODELS=(
 43:     "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_canny-fp16.safetensors"
 44:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_depth-fp16.safetensors"
 45:     "https://huggingface.co/kohya-ss/ControlNet-diff-modules/resolve/main/diff_control_sd15_depth_fp16.safetensors"
 46:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_hed-fp16.safetensors"
 47:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_mlsd-fp16.safetensors"
 48:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_normal-fp16.safetensors"
 49:     "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_openpose-fp16.safetensors"
 50:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_scribble-fp16.safetensors"
 51:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/control_seg-fp16.safetensors"
 52:     "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_canny-fp16.safetensors"
 53:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_color-fp16.safetensors"
 54:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_depth-fp16.safetensors"
 55:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_keypose-fp16.safetensors"
 56:     "https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_openpose-fp16.safetensors"
 57:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_seg-fp16.safetensors"
 58:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_sketch-fp16.safetensors"
 59:     #"https://huggingface.co/webui/ControlNet-modules-safetensors/resolve/main/t2iadapter_style-fp16.safetensors"
 60: )
 61: 
 62: ### DO NOT EDIT BELOW HERE UNLESS YOU KNOW WHAT YOU ARE DOING ###
 63: 
 64: function provisioning_start() {
 65:     DISK_GB_AVAILABLE=$(($(df --output=avail -m "${WORKSPACE}" | tail -n1) / 1000))
 66:     DISK_GB_USED=$(($(df --output=used -m "${WORKSPACE}" | tail -n1) / 1000))
 67:     DISK_GB_ALLOCATED=$(($DISK_GB_AVAILABLE + $DISK_GB_USED))
 68:     provisioning_print_header
 69:     provisioning_get_nodes
 70:     provisioning_install_python_packages
 71:     provisioning_get_models \
 72:         "${WORKSPACE}/storage/stable_diffusion/models/ckpt" \
 73:         "${CHECKPOINT_MODELS[@]}"
 74:     provisioning_get_models \
 75:         "${WORKSPACE}/storage/stable_diffusion/models/lora" \
 76:         "${LORA_MODELS[@]}"
 77:     provisioning_get_models \
 78:         "${WORKSPACE}/storage/stable_diffusion/models/controlnet" \
 79:         "${CONTROLNET_MODELS[@]}"
 80:     provisioning_get_models \
 81:         "${WORKSPACE}/storage/stable_diffusion/models/vae" \
 82:         "${VAE_MODELS[@]}"
 83:     provisioning_get_models \
 84:         "${WORKSPACE}/storage/stable_diffusion/models/esrgan" \
 85:         "${ESRGAN_MODELS[@]}"
 86:     provisioning_print_end
 87: }
 88: 
 89: function provisioning_get_nodes() {
 90:     for repo in "${NODES[@]}"; do
 91:         dir="${repo##*/}"
 92:         path="/opt/ComfyUI/custom_nodes/${dir}"
 93:         requirements="${path}/requirements.txt"
 94:         if [[ -d $path ]]; then
 95:             if [[ ${AUTO_UPDATE,,} != "false" ]]; then
 96:                 printf "Updating node: %s...\n" "${repo}"
 97:                 ( cd "$path" && git pull )
 98:                 if [[ -e $requirements ]]; then
 99:                     micromamba -n comfyui run ${PIP_INSTALL} -r "$requirements"
100:                 fi
101:             fi
102:         else
103:             printf "Downloading node: %s...\n" "${repo}"
104:             git clone "${repo}" "${path}" --recursive
105:             if [[ -e $requirements ]]; then
106:                 micromamba -n comfyui run ${PIP_INSTALL} -r "${requirements}"
107:             fi
108:         fi
109:     done
110: }
111: 
112: function provisioning_install_python_packages() {
113:     if [ ${#PYTHON_PACKAGES[@]} -gt 0 ]; then
114:         micromamba -n comfyui run ${PIP_INSTALL} ${PYTHON_PACKAGES[*]}
115:     fi
116: }
117: 
118: function provisioning_get_models() {
119:     if [[ -z $2 ]]; then return 1; fi
120:     dir="$1"
121:     mkdir -p "$dir"
122:     shift
123:     if [[ $DISK_GB_ALLOCATED -ge $DISK_GB_REQUIRED ]]; then
124:         arr=("$@")
125:     else
126:         printf "WARNING: Low disk space allocation - Only the first model will be downloaded!\n"
127:         arr=("$1")
128:     fi
129: 
130:     printf "Downloading %s model(s) to %s...\n" "${#arr[@]}" "$dir"
131:     for url in "${arr[@]}"; do
132:         printf "Downloading: %s\n" "${url}"
133:         provisioning_download "${url}" "${dir}"
134:         printf "\n"
135:     done
136: }
137: 
138: function provisioning_print_header() {
139:     printf "\n##############################################\n#                                            #\n#          Provisioning container            #\n#                                            #\n#         This will take some time           #\n#                                            #\n# Your container will be ready on completion #\n#                                            #\n##############################################\n\n"
140:     if [[ $DISK_GB_ALLOCATED -lt $DISK_GB_REQUIRED ]]; then
141:         printf "WARNING: Your allocated disk size (%sGB) is below the recommended %sGB - Some models will not be downloaded\n" "$DISK_GB_ALLOCATED" "$DISK_GB_REQUIRED"
142:     fi
143: }
144: 
145: function provisioning_print_end() {
146:     printf "\nProvisioning complete:  Web UI will start now\n\n"
147: }
148: 
149: # Download from $1 URL to $2 file path
150: function provisioning_download() {
151:     wget --header="Authorization: Bearer $HF_TOKEN" -qnc --content-disposition --show-progress -e dotbytes="${3:-4M}" -P "$2" "$1"
152: }
153: 
154: provisioning_start
```

## File: config/provisioning/seargedp-seargesdxl.sh
```bash
 1: #!/bin/bash
 2: 
 3: # This file will be sourced in init.sh
 4: 
 5: # https://raw.githubusercontent.com/ai-dock/comfyui/main/config/provisioning/seargedp-seargesdxl.sh
 6: 
 7: # Download SeargeSDXL and the required model files if they do not already exist
 8: 
 9: searge_git="https://github.com/SeargeDP/SeargeSDXL"
10: searge_dir="/opt/ComfyUI/custom_nodes/SeargeSDXL"
11: 
12: models_dir=/opt/ComfyUI/models
13: checkpoints_dir=${models_dir}/checkpoints
14: vae_dir=${models_dir}/vae
15: loras_dir=${models_dir}/loras
16: upscale_dir=${models_dir}/upscale_models
17: 
18: base_model_file=${checkpoints_dir}/sd_xl_base_1.0.safetensors
19: base_model_url=https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
20: refiner_model_file=${checkpoints_dir}/sd_xl_refiner_1.0.safetensors
21: refiner_model_url=https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors
22: sdxl_vae_file=${vae_dir}/sdxl_vae.safetensors
23: sdxl_vae_url=https://huggingface.co/madebyollin/sdxl-vae-fp16-fix/resolve/main/sdxl_vae.safetensors
24: offset_lora_file=${loras_dir}/sd_xl_offset_example-lora_1.0.safetensors
25: offset_lora_url=https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_offset_example-lora_1.0.safetensors
26: siax_upscale_file=${upscale_dir}/4x_NMKD-Siax_200k.pth
27: siax_upscale_url=https://huggingface.co/uwg/upscaler/resolve/main/ESRGAN/4x_NMKD-Siax_200k.pth
28: ultrasharp_upscale_file=${upscale_dir}/4x-UltraSharp.pth
29: ultrasharp_upscale_url=https://huggingface.co/uwg/upscaler/resolve/main/ESRGAN/4x-UltraSharp.pth
30: 
31: if [[ ! -d $searge_dir ]]; then
32:     git clone https://github.com/SeargeDP/SeargeSDXL $searge_dir
33: else
34:     cd $searge_dir && git pull
35: fi
36: 
37: if [[ ! -f ${base_model_file} ]]; then
38:     wget -O ${base_model_file} ${base_model_url}
39: fi
40: 
41: if [[ ! -f ${refiner_model_file} ]]; then
42:     wget -O ${refiner_model_file} ${refiner_model_url}
43: fi
44: 
45: if [[ ! -f ${sdxl_vae_file} ]]; then
46:     wget -O ${sdxl_vae_file} ${sdxl_vae_url}
47: fi
48: 
49: if [[ ! -f ${offset_lora_file} ]]; then
50:     wget -O ${offset_lora_file} ${offset_lora_url}
51: fi
52: 
53: if [[ ! -f ${siax_upscale_file} ]]; then
54:     wget -O ${siax_upscale_file} ${siax_upscale_url}
55: fi
56: 
57: if [[ ! -f ${ultrasharp_upscale_file} ]]; then
58:     wget -O ${ultrasharp_upscale_file} ${ultrasharp_upscale_url}
59: fi
```

## File: config/workflows/flux-comfyui-example.json
```json
  1: {
  2:   "last_node_id": 25,
  3:   "last_link_id": 40,
  4:   "nodes": [
  5:     {
  6:       "id": 13,
  7:       "type": "SamplerCustomAdvanced",
  8:       "pos": [
  9:         842,
 10:         215
 11:       ],
 12:       "size": {
 13:         "0": 355.20001220703125,
 14:         "1": 106
 15:       },
 16:       "flags": {},
 17:       "order": 9,
 18:       "mode": 0,
 19:       "inputs": [
 20:         {
 21:           "name": "noise",
 22:           "type": "NOISE",
 23:           "link": 37,
 24:           "slot_index": 0
 25:         },
 26:         {
 27:           "name": "guider",
 28:           "type": "GUIDER",
 29:           "link": 30,
 30:           "slot_index": 1
 31:         },
 32:         {
 33:           "name": "sampler",
 34:           "type": "SAMPLER",
 35:           "link": 19,
 36:           "slot_index": 2
 37:         },
 38:         {
 39:           "name": "sigmas",
 40:           "type": "SIGMAS",
 41:           "link": 20,
 42:           "slot_index": 3
 43:         },
 44:         {
 45:           "name": "latent_image",
 46:           "type": "LATENT",
 47:           "link": 23,
 48:           "slot_index": 4
 49:         }
 50:       ],
 51:       "outputs": [
 52:         {
 53:           "name": "output",
 54:           "type": "LATENT",
 55:           "links": [
 56:             24
 57:           ],
 58:           "shape": 3,
 59:           "slot_index": 0
 60:         },
 61:         {
 62:           "name": "denoised_output",
 63:           "type": "LATENT",
 64:           "links": null,
 65:           "shape": 3
 66:         }
 67:       ],
 68:       "properties": {
 69:         "Node name for S&R": "SamplerCustomAdvanced"
 70:       }
 71:     },
 72:     {
 73:       "id": 5,
 74:       "type": "EmptyLatentImage",
 75:       "pos": [
 76:         473,
 77:         450
 78:       ],
 79:       "size": {
 80:         "0": 315,
 81:         "1": 106
 82:       },
 83:       "flags": {},
 84:       "order": 0,
 85:       "mode": 0,
 86:       "outputs": [
 87:         {
 88:           "name": "LATENT",
 89:           "type": "LATENT",
 90:           "links": [
 91:             23
 92:           ],
 93:           "slot_index": 0
 94:         }
 95:       ],
 96:       "properties": {
 97:         "Node name for S&R": "EmptyLatentImage"
 98:       },
 99:       "widgets_values": [
100:         1024,
101:         1024,
102:         1
103:       ]
104:     },
105:     {
106:       "id": 22,
107:       "type": "BasicGuider",
108:       "pos": [
109:         559,
110:         125
111:       ],
112:       "size": {
113:         "0": 241.79998779296875,
114:         "1": 46
115:       },
116:       "flags": {},
117:       "order": 8,
118:       "mode": 0,
119:       "inputs": [
120:         {
121:           "name": "model",
122:           "type": "MODEL",
123:           "link": 39,
124:           "slot_index": 0
125:         },
126:         {
127:           "name": "conditioning",
128:           "type": "CONDITIONING",
129:           "link": 40,
130:           "slot_index": 1
131:         }
132:       ],
133:       "outputs": [
134:         {
135:           "name": "GUIDER",
136:           "type": "GUIDER",
137:           "links": [
138:             30
139:           ],
140:           "shape": 3,
141:           "slot_index": 0
142:         }
143:       ],
144:       "properties": {
145:         "Node name for S&R": "BasicGuider"
146:       }
147:     },
148:     {
149:       "id": 16,
150:       "type": "KSamplerSelect",
151:       "pos": [
152:         470,
153:         749
154:       ],
155:       "size": {
156:         "0": 315,
157:         "1": 58
158:       },
159:       "flags": {},
160:       "order": 1,
161:       "mode": 0,
162:       "outputs": [
163:         {
164:           "name": "SAMPLER",
165:           "type": "SAMPLER",
166:           "links": [
167:             19
168:           ],
169:           "shape": 3
170:         }
171:       ],
172:       "properties": {
173:         "Node name for S&R": "KSamplerSelect"
174:       },
175:       "widgets_values": [
176:         "euler"
177:       ]
178:     },
179:     {
180:       "id": 8,
181:       "type": "VAEDecode",
182:       "pos": [
183:         1248,
184:         192
185:       ],
186:       "size": {
187:         "0": 210,
188:         "1": 46
189:       },
190:       "flags": {},
191:       "order": 10,
192:       "mode": 0,
193:       "inputs": [
194:         {
195:           "name": "samples",
196:           "type": "LATENT",
197:           "link": 24
198:         },
199:         {
200:           "name": "vae",
201:           "type": "VAE",
202:           "link": 12
203:         }
204:       ],
205:       "outputs": [
206:         {
207:           "name": "IMAGE",
208:           "type": "IMAGE",
209:           "links": [
210:             9
211:           ],
212:           "slot_index": 0
213:         }
214:       ],
215:       "properties": {
216:         "Node name for S&R": "VAEDecode"
217:       }
218:     },
219:     {
220:       "id": 9,
221:       "type": "SaveImage",
222:       "pos": [
223:         1488,
224:         192
225:       ],
226:       "size": {
227:         "0": 985.3012084960938,
228:         "1": 1060.3828125
229:       },
230:       "flags": {},
231:       "order": 11,
232:       "mode": 0,
233:       "inputs": [
234:         {
235:           "name": "images",
236:           "type": "IMAGE",
237:           "link": 9
238:         }
239:       ],
240:       "properties": {},
241:       "widgets_values": [
242:         "ComfyUI"
243:       ]
244:     },
245:     {
246:       "id": 6,
247:       "type": "CLIPTextEncode",
248:       "pos": [
249:         375,
250:         221
251:       ],
252:       "size": {
253:         "0": 422.84503173828125,
254:         "1": 164.31304931640625
255:       },
256:       "flags": {},
257:       "order": 6,
258:       "mode": 0,
259:       "inputs": [
260:         {
261:           "name": "clip",
262:           "type": "CLIP",
263:           "link": 10
264:         }
265:       ],
266:       "outputs": [
267:         {
268:           "name": "CONDITIONING",
269:           "type": "CONDITIONING",
270:           "links": [
271:             40
272:           ],
273:           "slot_index": 0
274:         }
275:       ],
276:       "properties": {
277:         "Node name for S&R": "CLIPTextEncode"
278:       },
279:       "widgets_values": [
280:         "cute anime girl with massive fluffy fennec ears and a big fluffy tail blonde messy long hair blue eyes wearing a maid outfit with a long black dress with a gold leaf pattern and a white apron eating a slice of an apple pie in the kitchen of an old dark victorian mansion with a bright window and very expensive stuff everywhere"
281:       ]
282:     },
283:     {
284:       "id": 17,
285:       "type": "BasicScheduler",
286:       "pos": [
287:         468,
288:         867
289:       ],
290:       "size": {
291:         "0": 315,
292:         "1": 106
293:       },
294:       "flags": {},
295:       "order": 7,
296:       "mode": 0,
297:       "inputs": [
298:         {
299:           "name": "model",
300:           "type": "MODEL",
301:           "link": 38,
302:           "slot_index": 0
303:         }
304:       ],
305:       "outputs": [
306:         {
307:           "name": "SIGMAS",
308:           "type": "SIGMAS",
309:           "links": [
310:             20
311:           ],
312:           "shape": 3
313:         }
314:       ],
315:       "properties": {
316:         "Node name for S&R": "BasicScheduler"
317:       },
318:       "widgets_values": [
319:         "simple",
320:         20,
321:         1
322:       ]
323:     },
324:     {
325:       "id": 11,
326:       "type": "DualCLIPLoader",
327:       "pos": [
328:         28,
329:         239
330:       ],
331:       "size": {
332:         "0": 315,
333:         "1": 106
334:       },
335:       "flags": {},
336:       "order": 2,
337:       "mode": 0,
338:       "outputs": [
339:         {
340:           "name": "CLIP",
341:           "type": "CLIP",
342:           "links": [
343:             10
344:           ],
345:           "shape": 3,
346:           "slot_index": 0
347:         }
348:       ],
349:       "properties": {
350:         "Node name for S&R": "DualCLIPLoader"
351:       },
352:       "widgets_values": [
353:         "t5xxl_fp16.safetensors",
354:         "clip_l.safetensors",
355:         "flux"
356:       ]
357:     },
358:     {
359:       "id": 10,
360:       "type": "VAELoader",
361:       "pos": [
362:         864,
363:         384
364:       ],
365:       "size": {
366:         "0": 315,
367:         "1": 58
368:       },
369:       "flags": {},
370:       "order": 3,
371:       "mode": 0,
372:       "outputs": [
373:         {
374:           "name": "VAE",
375:           "type": "VAE",
376:           "links": [
377:             12
378:           ],
379:           "shape": 3,
380:           "slot_index": 0
381:         }
382:       ],
383:       "properties": {
384:         "Node name for S&R": "VAELoader"
385:       },
386:       "widgets_values": [
387:         "ae.safetensors"
388:       ]
389:     },
390:     {
391:       "id": 12,
392:       "type": "UNETLoader",
393:       "pos": [
394:         24,
395:         127
396:       ],
397:       "size": {
398:         "0": 315,
399:         "1": 82
400:       },
401:       "flags": {},
402:       "order": 4,
403:       "mode": 0,
404:       "outputs": [
405:         {
406:           "name": "MODEL",
407:           "type": "MODEL",
408:           "links": [
409:             38,
410:             39
411:           ],
412:           "shape": 3,
413:           "slot_index": 0
414:         }
415:       ],
416:       "properties": {
417:         "Node name for S&R": "UNETLoader"
418:       },
419:       "widgets_values": [
420:         "flux1-dev.safetensors",
421:         "default"
422:       ]
423:     },
424:     {
425:       "id": 25,
426:       "type": "RandomNoise",
427:       "pos": [
428:         470,
429:         611
430:       ],
431:       "size": {
432:         "0": 315,
433:         "1": 82
434:       },
435:       "flags": {},
436:       "order": 5,
437:       "mode": 0,
438:       "outputs": [
439:         {
440:           "name": "NOISE",
441:           "type": "NOISE",
442:           "links": [
443:             37
444:           ],
445:           "shape": 3
446:         }
447:       ],
448:       "properties": {
449:         "Node name for S&R": "RandomNoise"
450:       },
451:       "widgets_values": [
452:         814451063198230,
453:         "randomize"
454:       ]
455:     }
456:   ],
457:   "links": [
458:     [
459:       9,
460:       8,
461:       0,
462:       9,
463:       0,
464:       "IMAGE"
465:     ],
466:     [
467:       10,
468:       11,
469:       0,
470:       6,
471:       0,
472:       "CLIP"
473:     ],
474:     [
475:       12,
476:       10,
477:       0,
478:       8,
479:       1,
480:       "VAE"
481:     ],
482:     [
483:       19,
484:       16,
485:       0,
486:       13,
487:       2,
488:       "SAMPLER"
489:     ],
490:     [
491:       20,
492:       17,
493:       0,
494:       13,
495:       3,
496:       "SIGMAS"
497:     ],
498:     [
499:       23,
500:       5,
501:       0,
502:       13,
503:       4,
504:       "LATENT"
505:     ],
506:     [
507:       24,
508:       13,
509:       0,
510:       8,
511:       0,
512:       "LATENT"
513:     ],
514:     [
515:       30,
516:       22,
517:       0,
518:       13,
519:       1,
520:       "GUIDER"
521:     ],
522:     [
523:       37,
524:       25,
525:       0,
526:       13,
527:       0,
528:       "NOISE"
529:     ],
530:     [
531:       38,
532:       12,
533:       0,
534:       17,
535:       0,
536:       "MODEL"
537:     ],
538:     [
539:       39,
540:       12,
541:       0,
542:       22,
543:       0,
544:       "MODEL"
545:     ],
546:     [
547:       40,
548:       6,
549:       0,
550:       22,
551:       1,
552:       "CONDITIONING"
553:     ]
554:   ],
555:   "groups": [],
556:   "config": {},
557:   "extra": {
558:     "ds": {
559:       "scale": 1.2100000000000002,
560:       "offset": [
561:         15.746281987961769,
562:         -28.26147171780112
563:       ]
564:     }
565:   },
566:   "version": 0.4
567: }
```

## File: docker-compose.yaml
```yaml
 1: version: "3.8"
 2: # Compose file build variables set in .env
 3: services:
 4:   supervisor:
 5:     platform: linux/amd64
 6:     build:
 7:       context: ./build
 8:       args:
 9:         PYTHON_VERSION: ${PYTHON_VERSION:-3.10}
10:         PYTORCH_VERSION: ${PYTORCH_VERSION:-2.4.1}
11:         COMFYUI_BUILD_REF: ${COMFYUI_BUILD_REF:-}
12:         # Base on Python image which is base + python + jupyter
13:         IMAGE_BASE: ${IMAGE_BASE:-ghcr.io/ai-dock/python:${PYTHON_VERSION:-3.10}-v2-cuda-12.1.1-base-22.04}
14:       tags:
15:         - "ghcr.io/ai-dock/comfyui:${IMAGE_TAG:-pytorch-${PYTORCH_VERSION:-2.3.0}-py3.10-v2-cuda-12.1.1-base-22.04}"
16:         
17:     image: ghcr.io/ai-dock/comfyui:${IMAGE_TAG:-pytorch-${PYTORCH_VERSION:-2.3.0}-py3.10-v2-cuda-12.1.1-base-22.04}
18:     
19:     ## For Nvidia GPU's - You probably want to uncomment this
20:     #deploy:
21:     #  resources:
22:     #    reservations:
23:     #      devices:
24:     #        - driver: nvidia
25:     #          count: all
26:     #          capabilities: [gpu]
27:     
28:     devices:
29:       - "/dev/dri:/dev/dri"
30:       ## For AMD GPU
31:       #- "/dev/kfd:/dev/kfd"
32:       
33:               
34:     volumes:
35:       ## Workspace
36:       - ./workspace:${WORKSPACE:-/workspace/}:rshared
37:       # You can share /workspace/storage with other non-ComfyUI containers. See README
38:       #- /path/to/common_storage:${WORKSPACE:-/workspace/}storage/:rshared
39:       
40:       # Will echo to root-owned authorized_keys file;
41:       # Avoids changing local file owner
42:       - ./config/authorized_keys:/root/.ssh/authorized_keys_mount
43:       #- ./config/provisioning/default.sh:/opt/ai-dock/bin/provisioning.sh
44:       # In-container development
45:       - ./build/COPY_ROOT_1/opt/ai-dock/api-wrapper:/opt/ai-dock/api-wrapper
46:     ports:
47:         # SSH available on host machine port 2222 to avoid conflict. Change to suit
48:         - ${SSH_PORT_HOST:-2222}:22
49:         # Caddy port for service portal
50:         - ${SERVICEPORTAL_PORT_HOST:-1111}:${SERVICEPORTAL_PORT_HOST:-1111}
51:         # ComfyUI web interface
52:         - ${COMFYUI_PORT_HOST:-8188}:${COMFYUI_PORT_HOST:-8188}
53:         # Jupyter server
54:         - ${JUPYTER_PORT_HOST:-8888}:${JUPYTER_PORT_HOST:-8888}
55:         # Syncthing
56:         - ${SYNCTHING_UI_PORT_HOST:-8384}:${SYNCTHING_UI_PORT_HOST:-8384}
57:         - ${SYNCTHING_TRANSPORT_PORT_HOST:-22999}:${SYNCTHING_TRANSPORT_PORT_HOST:-22999}
58:    
59:     environment:
60:         # Don't enclose values in quotes
61:         - AUTO_UPDATE=${AUTO_UPDATE:-false}
62:         - DIRECT_ADDRESS=${DIRECT_ADDRESS:-127.0.0.1}
63:         - DIRECT_ADDRESS_GET_WAN=${DIRECT_ADDRESS_GET_WAN:-false}
64:         - WORKSPACE=${WORKSPACE:-/workspace}
65:         - WORKSPACE_SYNC=${WORKSPACE_SYNC:-false}
66:         - CF_TUNNEL_TOKEN=${CF_TUNNEL_TOKEN:-}
67:         - CF_QUICK_TUNNELS=${CF_QUICK_TUNNELS:-true}
68:         - CIVITAI_TOKEN=${CIVITAI_TOKEN:-}
69:         - HF_TOKEN=${HF_TOKEN:-}
70:         - WEB_ENABLE_AUTH=${WEB_ENABLE_AUTH:-true}
71:         - WEB_ENABLE_HTTPS=${WEB_ENABLE_HTTPS:-false}
72:         - WEB_USER=${WEB_USER:-user}
73:         - WEB_PASSWORD=${WEB_PASSWORD:-password}
74:         - SSH_PORT_HOST=${SSH_PORT_HOST:-2222}
75:         - SERVICEPORTAL_PORT_HOST=${SERVICEPORTAL_PORT_HOST:-1111}
76:         - SERVICEPORTAL_METRICS_PORT=${SERVICEPORTAL_METRICS_PORT:-21111}
77:         - SERVICEPORTAL_URL=${SERVICEPORTAL_URL:-}
78:         - COMFYUI_ARGS=${COMFYUI_ARGS:-}
79:         - COMFYUI_PORT_HOST=${COMFYUI_PORT_HOST:-8188}
80:         - COMFYUI_METRICS_PORT=${COMFYUI_METRICS_PORT:-28188}
81:         - COMFYUI_URL=${COMFYUI_URL:-}
82:         - JUPYTER_PORT_HOST=${JUPYTER_PORT_HOST:-8888}
83:         - JUPYTER_METRICS_PORT=${JUPYTER_METRICS_PORT:-28888}
84:         - JUPYTER_URL=${JUPYTER_URL:-}
85:         - SERVERLESS=${SERVERLESS:-false}
86:         - SYNCTHING_UI_PORT_HOST=${SYNCTHING_UI_PORT_HOST:-8384}
87:         - SYNCTHING_TRANSPORT_PORT_HOST=${SYNCTHING_TRANSPORT_PORT_HOST:-22999}
88:         - SYNCTHING_URL=${SYNCTHING_URL:-}
89:         #- PROVISIONING_SCRIPT=${PROVISIONING_SCRIPT:-}
```

## File: LICENSE.md
```markdown
 1: Custom Software License
 2: 
 3: Copyright © 2022-present Robert Ballantyne, trading as AI-Dock. All rights reserved.
 4: 
 5: Author and Licensor: Robert Ballantyne.
 6: 
 7: Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software") to use the Software for personal or commercial purposes, subject to the following conditions:
 8: 
 9: 1. Users may not modify the Software in any way that overrides the original code written by the author, except as explicitly instructed in the accompanying documentation provided by the author.
10: 
11: 2. Users may add additional code or modifications for their custom builds, provided that such additions do not override the original code written by the author.
12: 
13: 3. Distribution of the Software, including forks and source code, is permitted without explicit permission from the author. Hosting derivatives on a public registry, such as Docker Hub, is allowed, but users are not permitted to actively encourage the use of these derivatives by others without explicit permission from the author. Distribution of Docker images and templates derived from the Software is permitted only with explicit permission from the author. Permission may be revoked at any time without prior notice. To obtain permission for distribution of Docker images and templates, users must enter into a separate licensing agreement with the author.
14: 
15: 4. Users may not remove or alter any branding, trademarks, or copyright notices present in the Software, including hyperlinks to external resources such as the author's website or documentation, and links to third-party services. These hyperlinks and links shall remain intact and unaltered.
16: 
17: 5. Distribution of modified versions of the Software must prominently display a notice indicating that the Software has been modified from the original version and include appropriate attribution to the original author.
18: 
19: 6. Users may not engage in any activities that could lead to malicious imitation or misrepresentation of the Software, including but not limited to creating derivative works that attempt to pass off as the original Software or using the Software to mislead or deceive others.
20: 
21: 7. The author must ensure that the complete corresponding source code for the Software, including any modifications made by the author, remains publicly available at all times.
22: 
23: 8. Users who have been granted permission to modify and distribute the Software are responsible for ensuring that the complete corresponding source code for any modifications they make to the Software remains publicly available at all times when they distribute their versions of the Software. This requirement applies to both the original Software and any derivative works created based on the Software.
24: 
25: 9. This license applies only to the code originating from AI-Dock repositories, both inside and outside of containers. Other bundled software or dependencies should be viewed as separate entities and may be subject to their own respective licenses.
26: 
27: THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

## File: NOTICE.md
```markdown
 1: ## Notice:
 2: 
 3: I have chosen to apply a custom license to this software for the following reasons:
 4: 
 5: - **Uniqueness of Containers:** Common open-source licenses may not adequately address the nuances of software distributed within containers. My custom license ensures clarity regarding the separation of my code from bundled software, thereby respecting the rights of other authors.
 6: 
 7: - **Preservation of Source Code Integrity:** I am committed to maintaining the integrity of the source code while adhering to the spirit of open-source software. My custom license helps ensure transparency and accountability in my development practices.
 8: 
 9: - **Funding and Control of Distribution:** Some of the funding for this project comes from maintaining control of distribution. This funding model wouldn't be possible without limiting distribution in certain ways, ultimately supporting the project's mission.
10: 
11: - **Empowering Access:** Supported by controlled distribution, the mission of this project is to empower users with access to valuable tools and resources in the cloud, enabling them to utilize software that may otherwise require hardware resources beyond their reach.
12: 
13: I welcome sponsorship from commercial entities utilizing this software, although it is not mandatory. Your support helps sustain the ongoing development and improvement of this project.
14: 
15: You can sponsor this project at https://github.com/sponsors/ai-dock.
16: 
17: Your understanding and support are greatly appreciated.
```

## File: README.md
```markdown
 1: [![Docker Build](https://github.com/ai-dock/comfyui/actions/workflows/docker-build.yml/badge.svg)](https://github.com/ai-dock/comfyui/actions/workflows/docker-build.yml)
 2: 
 3: # AI-Dock + ComfyUI Docker Image
 4: 
 5: Run [ComfyUI](https://github.com/comfyanonymous/ComfyUI) in a highly-configurable, cloud-first AI-Dock container.
 6: 
 7: >[!NOTE]
 8: >These images do not bundle models or third-party configurations. You should use a [provisioning script](https://github.com/ai-dock/base-image/wiki/4.0-Running-the-Image#provisioning-script) to automatically configure your container. You can find examples, including `SD3` & `FLUX.1` setup, in `config/provisioning`.
 9: 
10: 
11: ## Documentation
12: 
13: All AI-Dock containers share a common base which is designed to make running on cloud services such as [vast.ai](https://link.ai-dock.org/vast.ai) as straightforward and user friendly as possible.
14: 
15: Common features and options are documented in the [base wiki](https://github.com/ai-dock/base-image/wiki) but any additional features unique to this image will be detailed below.
16: 
17: #### Version Tags
18: 
19: The `:latest` tag points to `:latest-cuda` and will relate to a stable and tested version.  There may be more recent builds
20: 
21: Tags follow these patterns:
22: 
23: ##### _CUDA_
24: - `:cuda-[x.x.x-base|runtime]-[ubuntu-version]`
25: 
26: ##### _ROCm_
27: - `:rocm-[x.x.x-runtime]-[ubuntu-version]`
28: 
29: ##### _CPU_
30: - `:cpu-[ubuntu-version]`
31: 
32: 
33: Browse [ghcr.io](https://github.com/ai-dock/comfyui/pkgs/container/comfyui) for an image suitable for your target environment. Alternatively, view a select range of [CUDA](https://hub.docker.com/r/aidockorg/comfyui-cuda) and [ROCm](https://hub.docker.com/r/aidockorg/comfyui-rocm) builds at DockerHub.
34: 
35: Supported Platforms: `NVIDIA CUDA`, `AMD ROCm`, `CPU`
36: 
37: ## Additional Environment Variables
38: 
39: | Variable                 | Description |
40: | ------------------------ | ----------- |
41: | `AUTO_UPDATE`            | Update ComfyUI on startup (default `false`) |
42: | `CIVITAI_TOKEN`          | Authenticate download requests from Civitai - Required for gated models |
43: | `COMFYUI_ARGS`           | Startup arguments. eg. `--gpu-only --highvram` |
44: | `COMFYUI_PORT_HOST`      | ComfyUI interface port (default `8188`) |
45: | `COMFYUI_REF`            | Git reference for auto update. Accepts branch, tag or commit hash. Default: latest release |
46: | `COMFYUI_URL`            | Override `$DIRECT_ADDRESS:port` with URL for ComfyUI |
47: | `HF_TOKEN`               | Authenticate download requests from HuggingFace - Required for gated models (SD3, FLUX, etc.) |
48: 
49: See the base environment variables [here](https://github.com/ai-dock/base-image/wiki/2.0-Environment-Variables) for more configuration options.
50: 
51: ### Additional Python Environments
52: 
53: | Environment    | Packages |
54: | -------------- | ----------------------------------------- |
55: | `comfyui`      | ComfyUI and dependencies |
56: | `api`          | ComfyUI API wrapper and dependencies |
57: 
58: 
59: The `comfyui` environment will be activated on shell login.
60: 
61: ~~See the base micromamba environments [here](https://github.com/ai-dock/base-image/wiki/1.0-Included-Software#installed-micromamba-environments).~~
62: 
63: ## Additional Services
64: 
65: The following services will be launched alongside the [default services](https://github.com/ai-dock/base-image/wiki/1.0-Included-Software) provided by the base image.
66: 
67: ### ComfyUI
68: 
69: The service will launch on port `8188` unless you have specified an override with `COMFYUI_PORT_HOST`.
70: 
71: You can set startup flags by using variable `COMFYUI_ARGS`.
72: 
73: To manage this service you can use `supervisorctl [start|stop|restart] comfyui`.
74: 
75: 
76: ### ComfyUI API Wrapper
77: 
78: This service is available on port `8188` and is a work-in-progress to replace previous serverless handlers which have been depreciated; Old Docker images and sources remain available should you need them.
79: 
80: You can access the api directly at `/ai-dock/api/` or you can use the Swager/openAPI playground at `/ai-dock/api/docs`.
81: 
82: >[!NOTE]
83: >All services are password protected by default. See the [security](https://github.com/ai-dock/base-image/wiki#security) and [environment variables](https://github.com/ai-dock/base-image/wiki/2.0-Environment-Variables) documentation for more information.
84: 
85: ## Pre-Configured Templates
86: 
87: **Vast.​ai**
88: 
89: - [comfyui:latest-cuda](https://link.ai-dock.org/template-vast-comfyui)
90: 
91: - [comfyui:latest-cuda + FLUX.1](https://link.ai-dock.org/template-vast-comfyui-flux)
92: 
93: - [comfyui:latest-rocm](https://link.ai-dock.org/template-vast-comfyui-rocm)
94: 
95: ---
96: 
97: _The author ([@robballantyne](https://github.com/robballantyne)) may be compensated if you sign up to services linked in this document. Testing multiple variants of GPU images in many different environments is both costly and time-consuming; This helps to offset costs_
```
