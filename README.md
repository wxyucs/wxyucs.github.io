[See it live](https://xyw.io)

## Photography images

Photography masters are stored in the Cloudflare R2 bucket `xyw-blog-images`
and published at `https://img.xyw.io`. Pages use `_includes/photo.html` to
request responsive AVIF, WebP, and JPEG variants through Cloudflare Image
Transformations.

Build 2400px progressive JPEG masters before uploading new photographs:

```sh
python3 scripts/build-photo-masters.py SOURCE_DIR OUTPUT_DIR \
  --manifest OUTPUT_DIR/manifest.json
```

Upload each generated master under `photos/<album>/` with `Content-Type:
image/jpeg` and `Cache-Control: public, max-age=31536000, immutable`, then add
its R2 path and generated dimensions to the post's `photos` front matter.
