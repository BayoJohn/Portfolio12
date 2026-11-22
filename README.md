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

## Site sources

- `templates/` contains the shared page shell and editable home, project and contact markup.
- `scripts/build.py` sets the navigation, section introductions, and canonical domain.
- `content/` is the publishing source. The original blog JavaScript files are retained as migration references.
- Old entry points such as `blog.html`, `blog_details.html`, `writing/`, `portfolio.html` and `contact.html` remain available. The current contact page uses a mailto form and direct email and social links.
