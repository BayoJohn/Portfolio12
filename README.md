# StackedByBayo

The site serves static HTML. The checked-in HTML is ready for static hosting. The Python build updates those pages from templates and Markdown.

## Publish an article

1. Create a Markdown file in `content/blog/`, `content/academy/`, or `content/reviews/`. Its lowercase, hyphen-separated filename becomes the URL slug.
2. Add a JSON front matter block between two lines containing `---`. Copy an existing file for the format. Required fields are `title`, `category`, `dateTime` (YYYY-MM-DD), and `excerpt`. Optional fields include `introduction`, `categories` (related-reading tags), `image` (absolute URL), `imageAlt`, `readTime`, and `draft` (boolean).
3. Write the body in Markdown. Use level-two headings for main sections since the template supplies the page heading. Fenced code blocks and tables are supported. Only use trusted content in this Git repository.
4. Run the build, review the generated pages and sitemap, and commit the Markdown and generated output together. Keep published filenames stable to preserve their URLs.

```sh
python3 -m pip install -r requirements.txt
python3 scripts/build.py
python3 -m http.server 8000
```

Use a virtual environment for the Python dependency if your system requires one. Open the preview at `http://localhost:8000/`. The custom 404 page and any server-side redirects depend on the production host.

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
