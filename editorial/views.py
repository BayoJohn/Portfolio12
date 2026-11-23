"""Private editorial forms. All stored and submitted text is escaped."""
from html import escape


def text(value):
    return escape(str(value or ""), quote=True)


def layout(title, body, *, logged_in=False):
    menu = ('<nav aria-label="Editorial"><a href="/admin/">Dashboard</a> '
            '<a href="/admin/categories/">Categories</a> <a href="/">Public site</a>'
            '<form method="post" action="/admin/logout/"><button>Log out</button></form></nav>') if logged_in else ""
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="robots" content="noindex,nofollow"><title>{text(title)} | StackedByBayo editorial</title>'
            '<link rel="stylesheet" href="/assets/css/editorial-admin.css"></head>'
            f'<body><header><strong>StackedByBayo Editorial</strong>{menu}</header>'
            f'<main><h1>{text(title)}</h1>{body}</main></body></html>')


def login(error=""):
    return layout("Administrator sign in", (f'<p role="alert">{text(error)}</p>' if error else "") +
                  '<form method="post" action="/admin/login/">'
                  '<label>Email<input type="email" name="email" autocomplete="username" required></label>'
                  '<label>Password<input type="password" name="password" autocomplete="current-password" required></label>'
                  '<button>Sign in</button></form>')


def dashboard(rows):
    counts = "".join(f'<div><dt>{label}</dt><dd>{sum(row["status"] == status for row in rows)}</dd></div>'
                     for status, label in (("published", "Published"), ("draft", "Drafts"), ("review", "In review")))
    items = "".join(
        f'<li><a href="/admin/articles/{row["id"]}/">{text(row["title"])}</a>'
        f'<span>{text(row["status"])} · {text(row["updated_at"][:10])}</span></li>'
        for row in sorted(rows, key=lambda item: item["updated_at"], reverse=True)
    )
    return layout("Article dashboard",
                  '<p><a class="button" href="/admin/articles/new/">New article</a></p>'
                  f'<dl class="counts">{counts}</dl><h2>Articles by last update</h2>'
                  + (f'<ul class="article-list">{items}</ul>' if items else '<p>No dashboard articles yet.</p>')
                  + '<p>Existing Markdown articles remain available in the public archive.</p>', logged_in=True)


FIELDS = (
    ("title", "Headline", 180, True), ("slug", "Slug", 100, True),
    ("summary", "Summary", 500, True), ("author", "Author", 120, True),
    ("tags", "Tags, separated by commas", 500, False),
    ("seo_description", "SEO description", 320, False),
    ("source_url", "Source URL", 1500, False),
    ("image_alt", "Featured image alt text", 300, False),
    ("image_caption", "Featured image caption", 500, False),
    ("image_credit", "Featured image credit", 300, False),
    ("body", "Article body in Markdown", 150000, True),
)
SECTIONS = {"news": "Tech News", "cybersecurity": "Cybersecurity", "ai": "AI",
            "gadgets": "Gadgets & Reviews", "software": "Software", "academy": "Tech Academy"}
TRANSITIONS = {"draft": {"review": "Submit for review"},
               "review": {"draft": "Return to draft", "published": "Publish article"},
               "published": {"draft": "Unpublish article"}}


def options(values, current):
    return "".join(f'<option value="{text(key)}"{" selected" if key == current else ""}>{text(label)}</option>'
                   for key, label in values)


def editor(row, categories, kinds, error=""):
    article_id = row.get("id")
    status = row.get("status", "draft")
    action = f'/admin/articles/{article_id}/' if article_id else '/admin/articles/new/'
    fields = []
    for name, label, limit, required in FIELDS:
        value = row.get(name)
        if name == "tags" and isinstance(value, list):
            value = ", ".join(value)
        attributes = f'name="{name}" maxlength="{limit}"' + (" required" if required else "")
        if name == "slug":
            attributes += ' pattern="[a-z0-9]+(-[a-z0-9]+)*"'
            if row.get("published_at"):
                attributes += " readonly"
        if name in {"summary", "body"}:
            control = f'<textarea {attributes} rows="{16 if name == "body" else 3}">{text(value)}</textarea>'
        else:
            control = f'<input {attributes} type="{"url" if name == "source_url" else "text"}" value="{text(value)}">'
        if name == "body":
            control += ('<small>Use Markdown for headings, lists, links, images, quotes, and fenced code. '
                        'Start headings at level two. Raw HTML is disabled.</small>')
        fields.append(f'<label>{label}{control}</label>')
    image = ""
    if row.get("image_key"):
        image = (f'<img class="cover" src="/admin/media/{row["image_key"]}.webp" alt="{text(row.get("image_alt"))}">'
                 '<label class="checkbox"><input type="checkbox" name="remove_image" value="1"> Remove current image</label>')
    category_options = options(((item["id"], item["name"]) for item in categories), row.get("category_id"))
    kind_options = options([("", "Unspecified"), *kinds.items()], row.get("article_type"))
    controls = f'<p><strong>Status:</strong> {text(status)}</p>'
    if article_id:
        controls += (f'<p><a href="{action}preview/">Preview saved article</a></p>'
                     f'<form method="post" action="{action}transition/">'
                     f'<input type="hidden" name="version" value="{text(row["updated_at"])}">'
                     + "".join(f'<button name="status" value="{target}">{label}</button> '
                               for target, label in TRANSITIONS[status].items()) + '</form>')
    if article_id and status != "published":
        controls += f'<p><a href="{action}delete/">Delete article</a></p>'
    form = (
        f'<form method="post" action="{action}" enctype="multipart/form-data">'
        f'<input type="hidden" name="version" value="{text(row.get("updated_at"))}">'
        f'<label>Category<select name="category_id" required>{category_options}</select></label>'
        f'<label>Article type<select name="article_type">{kind_options}</select></label>'
        + "".join(fields) + image +
        '<label>Featured image (JPEG, PNG, WebP, up to 2.8 MB)'
        '<input type="file" name="image" accept="image/jpeg,image/png,image/webp"></label>'
        '<button>Save article</button></form>'
    )
    notice = f'<p role="alert">{text(error)}</p>' if error else ""
    return layout("Edit article" if article_id else "New article", notice + controls + form, logged_in=True)


def categories_page(categories, error=""):
    forms = "".join(
        f'<form method="post" action="/admin/categories/">'
        f'<input type="hidden" name="id" value="{item["id"]}">'
        f'<label>Category name<input name="name" maxlength="80" required value="{text(item["name"])}"></label>'
        f'<p>Public section: {text(SECTIONS[item["section"]])}</p><button>Rename category</button></form>'
        for item in categories
    )
    notice = f'<p role="alert">{text(error)}</p>' if error else ""
    return layout("Categories", notice + '<h2>Add category</h2><form method="post" action="/admin/categories/">'
                  '<label>Category name<input name="name" maxlength="80" required></label>'
                  f'<label>Public section<select name="section">{options(SECTIONS.items(), "")}</select></label>'
                  '<button>Add category</button></form><h2>Existing categories</h2>' + forms, logged_in=True)


def confirm_delete(row):
    action = f'/admin/articles/{row["id"]}/'
    return layout("Delete article", f'<p>Delete <strong>{text(row["title"])}</strong> permanently?</p>'
                  f'<form action="{action}delete/" method="post">'
                  f'<input type="hidden" name="version" value="{text(row["updated_at"])}">'
                  f'<button>Delete permanently</button> <a href="{action}">Cancel</a></form>', logged_in=True)
