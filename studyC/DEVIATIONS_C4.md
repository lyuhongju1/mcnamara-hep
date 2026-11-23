2026-11-22: run interrupted by OS memory pressure (Sonnet 4.5 59/80, GPT-5.5 0/80); restarted with the same run ids.
2026-11-23: all GPT-5.5 runs failed with 401 'API key has expired' (the key was rotated after C3). The Sonnet 4.5 half completed (80/80). H6 is pooled over both models per the prereg, so it is not evaluated until the GPT-5.5 half runs with a new key; the Sonnet-only numbers are reported as interim and descriptive.
2026-11-23: new OpenAI key; GPT-5.5 half run from scratch (no GPT runs had completed).
2026-11-23: GPT-5.5 half interrupted by OS memory pressure at 35/80; restarted with the same run ids.
2026-11-23: interrupted again at 76/80; final 4 runs completed in the foreground with the same run ids.
2026-11-23: out_c4gpt/S7_gas__PN-Y-H__gpt-5.5__r2/result.json was corrupted (two JSON objects; a process from the killed background job overlapped the foreground run). Deleted and re-run with the same run id. No other file was affected; all others parse.
