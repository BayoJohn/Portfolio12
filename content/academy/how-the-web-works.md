---
{
  "title": "How the Web Works, From the Address Bar to the Page",
  "articleType": "tutorial",
  "author": "StackedByBayo",
  "evergreen": true,
  "category": "Networking",
  "categories": ["networking", "web"],
  "excerpt": "Follow one web request to see what DNS, IP addresses, routers, HTTPS and servers each do.",
  "sources": [
    {"label": "ICANN on the Domain Name System", "url": "https://www.icann.org/resources/pages/dns-2022-09-13-en"},
    {"label": "MDN on how the Internet works", "url": "https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/How_does_the_Internet_work"},
    {"label": "MDN on how the web works", "url": "https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works"},
    {"label": "RFC 2606 on reserved example domains", "url": "https://www.rfc-editor.org/rfc/rfc2606.html"}
  ]
}
---

You enter `https://example.com/` and a page appears. Between those two moments, your device finds an address, sends data across several networks, and asks a server for a resource. Following one request gives you a way to make sense of the error messages you see when a page fails to load.

## What you’ll learn

You’ll trace a first visit to a website and see where DNS, IP, routers and HTTP fit. To try the exercise, use a desktop browser with developer tools. You can follow the explanation on a phone, too.

## DNS finds an address for the name

The URL contains a scheme (`https`), a hostname (`example.com`) and a path (`/`). The hostname tells the browser which site to contact. The path tells the site which resource the browser wants.

To send packets, the device needs an IP address. If an address is already cached, the lookup can be short. Otherwise, a DNS resolver can ask the relevant name servers and return an answer. A name can have more than one address, and the answer can change over time. This is one reason two people can reach the same named service through different infrastructure.

## Routers move packets between networks

An IP address tells the network where a packet is headed. On a typical home connection, your device sends traffic destined for the wider internet to its local router. The router forwards the packet onward, and other routers choose subsequent hops. Each router can make its own forwarding decision based on the destination, and the return traffic may follow a different path.

The internet connects many networks. The web runs on top of that infrastructure and uses HTTP to exchange resources. Other applications can use the same networks for different purposes, such as sending mail.

## HTTPS protects the request and response

The browser establishes a secure connection if it needs a new one. With HTTPS, TLS protects data in transit and lets the browser check that the server presents a certificate valid for the hostname. That check helps establish who the browser is talking to. You still need to decide whether you trust the site itself.

The browser then sends an HTTP request. In this example it asks for `/` with the `GET` method. The server, or an intermediary such as a content delivery network, returns a response with a status, headers and, when applicable, a body. A `200` usually indicates a successful request. A `404` means a server answered but could not find the requested resource. In both cases, the browser got far enough to receive an HTTP response.

HTML gives the browser a document to render. As it reads the HTML, it may request stylesheets, scripts and images, reuse cached copies, or run scripts that request more data. One page visit often involves several requests.

## Try it in your browser

1. Open the browser’s developer tools and select **Network**.
2. Visit `https://example.com/`. If the panel is empty, reload with it open.
3. Select the document request. Look for the request URL, method and status code. If a timing panel is available, see which parts of the request it records.
4. Repeat on a familiar site. Compare the document request with a stylesheet or image request. Notice which requests use a different hostname or were served from cache.

!!! note "Timing can vary"
    A reload might reuse an existing connection or a cached result. Missing DNS or connection timing can reflect that reuse.

## Key takeaways

When a site fails, start with the earliest layer you can confirm. If the hostname cannot be resolved, look at the name and DNS. If you receive an HTTP status, the browser reached something that could answer the request. If text loads but images do not, inspect those individual requests. Continue with the [Linux troubleshooting article](../../blog/troubleshooting-the-problems-that-actually-taught-me-linux/) to see how the same approach applies to a local service.
