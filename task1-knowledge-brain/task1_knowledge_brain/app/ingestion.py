import asyncio, hashlib
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from db import connect

def parse_article(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for node in soup(["script","style","nav","footer","header","noscript"]):
        node.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    title = soup.title.get_text(" ",strip=True) if soup.title else "Untitled article"
    chunks, buf = [], []
    heading = title
    for el in main.find_all(["h1","h2","h3","p","li","td","th"]):
        text = el.get_text(" ",strip=True)
        if not text: continue
        if el.name in ("h1","h2","h3"):
            if buf: chunks.append((heading," ".join(buf))); buf=[]
            heading = text
        else:
            buf.append(text)
            if sum(len(x) for x in buf) >= 1400:
                chunks.append((heading," ".join(buf))); buf=[]
    if buf: chunks.append((heading," ".join(buf)))
    if not chunks:
        text = main.get_text(" ",strip=True)
        if text: chunks=[(title,text[:1800])]
    images = [{"alt":i.get("alt",""),"src":i.get("src","")} for i in main.find_all("img") if i.get("src")]
    return title, chunks, images

async def crawl_sitemap(sitemap_url: str, max_pages: int = 20):
    headers={"User-Agent":"AITechConsultantCapstone/1.0 (polite educational crawler)"}
    async with httpx.AsyncClient(timeout=20,follow_redirects=True,headers=headers) as client:
        response=await client.get(sitemap_url); response.raise_for_status()
        sm=BeautifulSoup(response.text,"xml")
        urls=[x.get_text(strip=True) for x in sm.find_all("loc")]
        urls=list(dict.fromkeys(u for u in urls if urlparse(u).scheme=="https"))[:max_pages]
        stats={"discovered":len(urls),"added":0,"updated":0,"unchanged":0,"failed":[]}
        for url in urls:
            try:
                with connect() as c:
                    old=c.execute("SELECT content_hash FROM articles WHERE url=?",(url,)).fetchone()
                    c.execute("INSERT INTO ingestion(url,status,attempts,error,updated_at) VALUES(?,'fetching',1,NULL,CURRENT_TIMESTAMP) ON CONFLICT(url) DO UPDATE SET status='fetching',attempts=attempts+1,error=NULL,updated_at=CURRENT_TIMESTAMP",(url,))
                await asyncio.sleep(0.25)
                page_response=await client.get(url); page_response.raise_for_status()
                title,chunks,images=parse_article(page_response.text)
                body="\n\n".join(f"{h}\n{t}" for h,t in chunks)
                digest=hashlib.sha256(body.encode()).hexdigest()
                if old and old["content_hash"]==digest:
                    stats["unchanged"]+=1
                    with connect() as c: c.execute("UPDATE ingestion SET status='unchanged',updated_at=CURRENT_TIMESTAMP WHERE url=?",(url,))
                    continue
                with connect() as c:
                    c.execute("INSERT INTO articles(url,title,content,content_hash,lastmod,active,fetched_at) VALUES(?,?,?,?,NULL,1,CURRENT_TIMESTAMP) ON CONFLICT(url) DO UPDATE SET title=excluded.title,content=excluded.content,content_hash=excluded.content_hash,active=1,fetched_at=CURRENT_TIMESTAMP",(url,title,body,digest))
                    c.execute("DELETE FROM chunks WHERE url=?",(url,))
                    for idx,(heading,content) in enumerate(chunks):
                        c.execute("INSERT OR IGNORE INTO chunks(url,title,heading,content,chunk_index) VALUES(?,?,?,?,?)",(url,title,heading,content,idx))
                    c.execute("UPDATE ingestion SET status='complete',error=NULL,updated_at=CURRENT_TIMESTAMP WHERE url=?",(url,))
                stats["updated" if old else "added"]+=1
            except Exception as exc:
                stats["failed"].append({"url":url,"error":str(exc)[:180]})
                with connect() as c:
                    c.execute("INSERT INTO ingestion(url,status,attempts,error,updated_at) VALUES(?,'failed',1,?,CURRENT_TIMESTAMP) ON CONFLICT(url) DO UPDATE SET status='failed',error=excluded.error,updated_at=CURRENT_TIMESTAMP",(url,str(exc)[:500]))
        return stats
