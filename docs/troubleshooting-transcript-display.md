# Troubleshooting: Transcript Display Issue

## Problem Description

Transcripts were not displaying on the Azure-deployed site (https://calm-ocean-061ff161e.1.azurestaticapps.net/items/dg_1750784116t.html) despite working correctly on the local Jekyll development server (http://127.0.0.1:4000/items/dg_1750784116t.html).

## Symptoms

- Local Jekyll build: Transcript displayed correctly, generated HTML file size ~459KB
- Azure deployed site: Transcript missing, generated HTML file size only ~66KB
- No build errors in Azure Static Web Apps deployment
- Template project (https://gentle-ground-0283de21e.3.azurestaticapps.net) working correctly with identical data

## Investigation Process

1. **Verified data integrity**: Confirmed that `_data/gdp-oh-metadata-with-video.csv` contained the correct `object_transcript` field (column 34) with value `dg_1750784116.csv`

2. **Added debug output**: Modified `_layouts/item/transcript.html` to output the values of `page.object-transcript` and conditional branch execution

3. **Key finding**: Debug output showed:
   ```html
   <!-- DEBUG: object-transcript="" objectid="dg_1750784116t" -->
   <!-- DEBUG: Branch 3 (fallback) - items.size=0 -->
   ```
   The `page.object-transcript` variable was empty, causing the layout to fall back to looking for `site.data.transcripts[page.objectid]` instead of the correct transcript file.

4. **Field name inspection**: Created a test page to enumerate all fields available in the generated page object. This revealed:
   - The page object had `object_transcript` (with underscore): `"dg_1750784116.csv"`
   - But NOT `object-transcript` (with hyphen)

## Root Cause

**Jekyll's CollectionBuilder page generator does not convert CSV field names with underscores to hyphens when assigning them to page data.**

The `_plugins/cb_page_gen.rb` plugin assigns CSV row data directly to the page's `@data` hash:

```ruby
# Line 206 in cb_page_gen.rb
@data = record
```

This means CSV fields like `object_transcript` remain as `page.object_transcript` in Liquid templates, rather than being converted to `page.object-transcript` as would happen with standard Jekyll front matter.

The original layout code was checking:
```liquid
{% if page.object-transcript contains ".csv"%}
```

But it should have been:
```liquid
{% if page.object_transcript contains ".csv"%}
```

## Solution

Changed all references from `page.object-transcript` (hyphen) to `page.object_transcript` (underscore) in `_layouts/item/transcript.html`:

**Before:**
```liquid
{% if page.object-transcript contains ".csv"%}
{% assign transcript = page.object-transcript | remove: ".csv" %}
{% assign items = site.data.transcripts[transcript] %}
{% elsif page.object-transcript %}
{% assign items = site.data.transcripts[page.object-transcript] %}
{% else %}
{% assign items = site.data.transcripts[page.objectid] %}
{% endif %}
```

**After:**
```liquid
{% if page.object_transcript contains ".csv"%}
{% assign transcript = page.object_transcript | remove: ".csv" %}
{% assign items = site.data.transcripts[transcript] %}
{% elsif page.object_transcript %}
{% assign items = site.data.transcripts[page.object_transcript] %}
{% else %}
{% assign items = site.data.transcripts[page.objectid] %}
{% endif %}
```

## Verification

After the fix:
- Generated HTML file size increased from 66KB to 459KB
- Transcript content appeared in the built page
- Debug output confirmed the correct branch executed:
  ```html
  <!-- DEBUG: object_transcript="dg_1750784116.csv" objectid="dg_1750784116t" -->
  <!-- DEBUG: Branch 1 underscore - transcript="dg_1750784116" items.size=332 -->
  ```

## Commits

- **GCCB-Georgia-Dentel-Project**: [58befc4](https://github.com/Digital-Grinnell/GCCB-Georgia-Dentel-Project/commit/58befc4)
- **GCCB-project-template**: [f73a213](https://github.com/Digital-Grinnell/GCCB-project-template/commit/f73a213)

## Lessons Learned

1. **CSV field naming**: When CollectionBuilder generates pages from CSV metadata, field names with underscores remain as underscores in Liquid templates, unlike standard Jekyll front matter which converts them to hyphens.

2. **Debugging technique**: Using HTML comments with Liquid output (`<!-- DEBUG: variable="{{ page.variable }}" -->`) is effective for diagnosing page generation issues, especially when local builds work but deployed builds don't.

3. **Test page isolation**: Creating minimal test pages with only the problematic Liquid logic helps isolate whether the issue is with the data, the logic, or the page generation process.

4. **Environment differences**: What works locally may not work in deployed environments. Always test the actual generated static files, not just the development server output.

## Related Files

- `_layouts/item/transcript.html` - Main transcript layout (fixed)
- `_plugins/cb_page_gen.rb` - CollectionBuilder page generator (assigns CSV data to pages)
- `_data/gdp-oh-metadata-with-video.csv` - Metadata CSV with `object_transcript` field
- `_data/transcripts/*.csv` - Individual transcript data files

---

*Issue resolved: January 14, 2026*
