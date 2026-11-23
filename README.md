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
