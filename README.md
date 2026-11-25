# StackedByBayo

The site serves static HTML. The checked-in HTML is ready for static hosting. The Python build updates those pages from templates and Markdown.

## Publish an article

1. Create a Markdown file in `content/blog/`, `content/academy/`, or `content/reviews/`. Its lowercase, hyphen-separated filename becomes the URL slug.
2. Add a JSON front matter block between two lines containing `---`. Copy an existing file for the format. Required fields are `title`, `category`, and `excerpt`. Include `dateTime` (YYYY-MM-DD) for dated articles. Optional fields include `introduction`, `categories` (related-reading tags), `image` (absolute URL), `imageAlt`, `readTime`, and `draft` (boolean).
3. Write the body in Markdown. Use level-two headings for main sections since the template supplies the page heading. Fenced code blocks and tables are supported. Only use trusted content in this Git repository.
4. Run the build, review the generated pages and sitemap, and commit the Markdown and generated output together. Keep published filenames stable to preserve their URLs.

```sh
python3 -m pip install -r requirements.txt
python3 scripts/build.py
python3 -m http.server 8000
```

Use a virtual environment for the Python dependency if your system requires one. Open the preview at `http://localhost:8000/`. The custom 404 page and any server-side redirects depend on the production host.

## Homepage edition

Edit `content/home-edition.json` to select the lead story, two secondary stories, Editor’s Picks, In Focus links, and featured stories for each editorial collection. Use the existing article paths, including the trailing slash. Add matching `homeTopics` to an article to make it eligible for the homepage and its selected sections. Set `homeAnalysis` to true for analysis. The date field records publication by StackedByBayo. Use an optional `date` on each source entry to record the source’s publication date.

## Software hub

Edit `content/software-apps.json` to update directory entries. Keep publisher links on official sites and point each `article` field to a published Software article slug. Software articles use the existing `content/blog/` collection and article URLs. Set `softwareFormat` to `news`, `guide`, `comparison`, `overview`, or `hands-on`, and add platform or subject tags to place the article in filters. News can include `softwareEventDate` for the release or announcement date. For reviews, use `softwareReview` with fields such as `platforms`, `license`, `limitations`, `verdict`, and `evaluation`. Reserve the hands-on label for documented testing.

## Cybersecurity desk

New desk articles use `securityDesk` tags for the section’s editorial collections. Use `securityEventDate` for a verified advisory, disclosure or release date, and keep the article's original publication date in `dateTime`. The existing `security` fields and Markdown tables support affected products, mitigations and official references.

`content/security-vulnerabilities.json` is a manually reviewed selection. Record the actual review date in `checked`. Attribute any numeric `cvss` score with its version and source, and use `kev_added` only when an authoritative source confirms both exploitation and the catalogue date. Advisory dates refer to the cited advisory. Remove obsolete `alert` labels during editorial review. The table and filters consume local records. A future NVD, KEV or vendor integration can supply the same fields after verification and normalization. The deployed page makes no catalogue API calls.

## Publication information

The About, Contact, Editorial Standards, Corrections, Privacy and Disclosures pages use templates in `templates/`. The shared route labels and verified contact address are in `scripts/build.py`. The legacy `contact.html` URL leads to the email-based Contact page.

For a material factual correction to a Markdown article, add a `corrections` entry with its actual `date` (YYYY-MM-DD) and a factual `note` describing the change. The build displays the dated note and uses the later of the correction or `updatedTime` for article metadata. For database-managed articles, place a dated correction note in the existing article body. The dashboard and data model require no changes.

Before publishing the policy pages, verify the production hosting and analytics settings, provider log retention, email handling and retention, and any advertising, affiliate or sponsorship arrangements that are managed outside this repository. Confirm the public contact mailbox is monitored and approve the editorial commitments.

## Article reading template

The article template adds a table of contents to articles with three or more main sections and to tutorials with headings. Use Markdown headings in order, starting at level two. Keep heading text and any explicitly assigned IDs stable after publishing. Use fenced code blocks, Markdown tables, and `!!! note "Title"` followed by an indented paragraph for callouts. For inline captions, use trusted `figure` and `figcaption` HTML. Give embedded iframes descriptive titles and use native controls with captions or transcripts where applicable.

Optional editorial fields in the JSON front matter:

| Field | Use |
| --- | --- |
| `articleType` | `reporting`, `news-summary`, `commentary`, `security-update`, `review`, or `tutorial`. |
| `updatedTime` | An actual update date in YYYY-MM-DD format, on or after publication. |
| `author`, `authorURL`, `authorBio` | Byline details. The existing publication author is used when the byline is omitted. |
| `imageAlt`, `imageCaption`, `imageCredit`, `imageCreditURL` | Supply descriptive alt text for meaningful cover images and credit information as required by the license. |
| `sources` | A list of objects with `label` and absolute `url` fields. |
| `security` | Optional `severity`, `affectedProducts`, `audience`, `recommendedActions`, and `advisories`. Add an authoritative `severitySource` URL whenever a rating is shown. |
| `review` | Optional `productOverview`, `specifications`, `advantages`, `limitations`, `verdict`, and `testingDisclosure`. State whether you tested the product hands-on or evaluated it through research. |
| `tutorial` | Optional `prerequisites`, `troubleshooting`, and `resources`. Use body headings for the steps. |

`advisories` and `resources` use the same link format as `sources`. Structured detail values accept a string or a list of strings. For `severity`, use the source's stated rating as a string.

### Editorial formats

Use the section sequence below as a Markdown outline. Write specific headings when they help readers scan. Open with a short introduction that explains the story or the task. Define unfamiliar terms on first use and include enough detail for readers who want to go deeper.

| Format | Section order | What to establish |
| --- | --- | --- |
| Technology News | What happened → Important details → Why it matters → What’s next | Attribute confirmed details and distinguish scheduled events from expectations. |
| Cybersecurity | What happened → Who is affected → Technical explanation → Recommended actions → Sources | Name affected versions or audiences when verified. Ground severity and mitigation guidance in official advisories. |
| Gadget Reviews | Overview → Features → Strengths → Limitations → Verdict | Disclose whether the evaluation was hands-on or research-based. Tie conclusions to the evidence and to the people the product suits. |
| Tech Academy | What you’ll learn → Prerequisites → Explanation → Practical examples → Key takeaways | State the starting knowledge, tools and environment. Use fenced code with a language identifier, and explain the result readers should expect. |

Provide the actual author, publication date and supporting links when preparing an article. For an undated evergreen Markdown guide, set `"evergreen": true` and omit `dateTime`. The guide appears in its collection, and dated articles take priority in chronological listings. Add references through the existing `sources` field. Use the existing security advisory and tutorial resource fields where appropriate. Use blockquotes for attributed quotations and Markdown admonitions for tips or cautions.

## Site sources

- `templates/` contains the shared page shell and editable home, project and contact markup.
- `scripts/build.py` sets the navigation, section introductions, and canonical domain.
- `content/` is the publishing source. The original blog JavaScript files are retained as migration references.
- Old entry points such as `blog.html`, `blog_details.html`, `writing/`, `portfolio.html` and `contact.html` remain available. The current contact page uses a mailto form and direct email and social links.

## Editorial dashboard on Vercel

The Vercel Python function serves `/admin/` and renders the existing publication templates
with published database records. Static assets and the other public pages still use the
checked-in HTML. The original Markdown articles retain their URLs and stay read-only
in the dashboard. New articles can be managed entirely through the dashboard.

### Production setup

1. In Supabase, create a project. In its SQL Editor, run
   [the editorial migration](migrations/001_editorial.sql) once. This creates the managed
   article, category, and session tables and a private `editorial-images` bucket.
2. Under Supabase Authentication, enable email/password sign-in and disable public signups.
   Create and confirm the administrator under Authentication → Users. Copy that user's UUID.
   Use a strong unique password and leave the provider's sign-in rate limits enabled.
3. In the existing Vercel project's **Production** environment, set the variables listed
   below. Enter the secret value directly in Vercel.
4. In Vercel, check Settings → Environments → Production → Branch Tracking.
   Verify that the existing GitHub repository's `main` branch is selected and that the Vercel
   project root is this repository. Use the build and output settings in `vercel.json`.
5. Once deployed, open `https://stackedbybayo.site/admin/login/` on the canonical domain.
   A working session redirects to `https://stackedbybayo.site/admin/`.
   Test the workflow with a disposable draft before publishing real content.

| Production variable | Value |
| --- | --- |
| `EDITORIAL_ORIGIN` | `https://stackedbybayo.site` |
| `SUPABASE_URL` | The HTTPS project URL from Supabase |
| `SUPABASE_PUBLISHABLE_KEY` | The publishable key or legacy anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | The legacy service-role JWT, kept server-only |
| `EDITORIAL_ADMIN_IDS` | Comma-separated UUIDs of the provisioned Supabase administrator users |

Editors save drafts, submit them for review, and explicitly publish from the saved
article screen. The dashboard accepts Markdown and JPEG, PNG, or WebP covers up to
2.8 MB. Published URLs remain stable. Unpublishing removes the managed article and its
cover from public access. Category management supports adding categories to existing
public sections and renaming them. Delete requires confirmation and an unpublished status.

If production integration checks are pending, verify login and logout, unauthorized route
access, public and private image visibility, and the full draft-to-published workflow
before using the dashboard for real content. The public site can fall back to its original
articles if Supabase is unavailable. The admin fails closed when configuration is missing.

### Local checks

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build.py
python3 scripts/package_site.py
```

The tests use an isolated provider fixture. They do not connect to a production service.

## External technology headlines

The Tech News page reads a same-origin JSON snapshot at `/assets/data/tech-news.json`. It makes one request for that file and never requests publisher feeds from visitors’ browsers. The collector stores headlines, publisher attribution, direct HTTPS links, source dates when valid, topics and first-fetch timestamps. The current sources supply no descriptions or images to the snapshot.

- [Electronic Frontier Foundation RSS](https://www.eff.org/rss/updates.xml) and [copyright policy](https://www.eff.org/copyright). EFF licenses its original material under CC BY 4.0 unless otherwise noted. The feed shows the publisher and links to the original headline.
- [NASA Technology RSS](https://www.nasa.gov/technology/feed/) and [media usage guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/). The feed shows NASA headlines and direct links. Third-party imagery, logos and article text are excluded.

`Refresh Tech News` is scheduled at minute 23 every four hours UTC on GitHub Actions. Repository users with the required GitHub permissions can also run it manually on `main`. The workflow serializes runs and commits only snapshot changes using GitHub’s repository-scoped token. It needs GitHub Actions enabled and permission to push the snapshot to `main` under the existing branch rules. GitHub may delay scheduled jobs and can disable them after 60 days of inactivity in a public repository. See the [GitHub schedule documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

Vercel serves the snapshot from the existing production deployment. If the connected Vercel project does not automatically deploy bot-authored commits, an administrator can test a [Vercel deploy hook](https://vercel.com/docs/deploy-hooks) for the existing project and `main` branch. Save its URL only as the GitHub Actions secret `VERCEL_NEWS_DEPLOY_HOOK` if that route is supported by the project’s plan and collaboration settings. A hook does not replace project authorization. See the [Vercel collaboration requirements](https://vercel.com/docs/deployments/troubleshoot-project-collaboration).

The page initially shows eight headlines and can load up to 48 from the snapshot, with at most 24 per source. Recent cached items survive an upstream outage and expire after 14 days, using the publication timestamp where available. Duplicate links use a stable hash with common tracking parameters, fragment, query order, the `www` prefix and trailing slash ignored. Unrecognised or conflicting topic labels fall back to the publisher’s broad subject area.

For a manual check without updating the repository snapshot, run `python3 scripts/collect_news.py --output /tmp/stackedbybayo-news.json`. Run the production packaging command with `python3 scripts/package_site.py`.
