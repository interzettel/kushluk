# Failure Matrix

Kushluk must fail visibly and usefully.

## Severity

### INFO
A non-essential source is unavailable and the edition remains materially complete.

Action: local log; optional small editorial omission.

### DEGRADED
A meaningful source or feature is unavailable, but a useful edition can still be produced.

Action: continue, reflow content, record degradation, notify when the missing source affects user expectations.

### FAILED
The core edition or requested delivery cannot complete.

Action: preserve generated artefacts, notify explicitly, attempt configured fallback where safe.

## Initial failure catalogue

| Failure | Severity | Edition behaviour | User notification |
|---|---|---|---|
| Weather source unavailable | DEGRADED | Use cached/redundant source or omit/reflow | Only if no weather result can be produced |
| Location unknown | DEGRADED | Use configured default location | Mention fallback when relevant |
| Calendar connector unavailable | DEGRADED | Remove calendar block, reflow | Yes |
| Task connector unavailable | DEGRADED | Remove task block, reflow | Yes if normally enabled |
| One RSS/news source unavailable | INFO | Continue with other sources | No, unless source is explicitly required |
| All editorial sources unavailable | FAILED/DEGRADED | Produce practical edition only if possible | Yes |
| X/social connector unavailable | INFO/DEGRADED | Continue without social candidates | Notify only if user made it required |
| LLM/editorial model unavailable | DEGRADED/FAILED | Use deterministic/simple fallback if available | Yes if quality materially reduced or edition fails |
| Renderer failure | FAILED | Keep canonical publication data | Yes |
| Layout overflow after cut retries | FAILED | Do not print malformed page; preserve debug artefact | Yes |
| Image unavailable/unsuitable | INFO/DEGRADED | Try another verified asset or switch to text-led layout | Only if imagery was essential to the promised content |
| Image attribution/rights state unresolved | DEGRADED | Do not use the asset; substitute or go text-only | No unless it materially changes the edition |
| Printer offline | FAILED delivery | Send digital fallback | Yes |
| Printer out of paper (detectable) | FAILED delivery | Send digital fallback | Yes |
| Requested paper/profile incompatible with detectable printer media | FAILED delivery/DEGRADED | Do not knowingly submit a bad job; preserve edition and use configured fallback | Yes, with remediation |
| Actual paper colour/stock cannot be detected | INFO | Trust explicit configured paper profile; do not invent sensor knowledge | No |
| Duplex unsupported | INFO | Use single-sided fallback | No, unless user required duplex |
| Email fallback unavailable | FAILED delivery | Preserve edition locally; try later channels if configured | Yes |
| Travel state uncertain | INFO | Default conservatively according to user policy | Only if it changes delivery decision |
| Secret/token expired | DEGRADED/FAILED | Disable affected connector | Yes, with remediation |
| Duplicate/retried scheduled run detected | INFO | Reuse/resume the edition state and suppress duplicate print submission unless explicitly reprinted | No, unless intervention is required |
| Archive write failure | FAILED | Do not silently discard edition state | Yes |

## Error message style

Messages must state:
1. what failed;
2. what Kushluk did instead;
3. whether the edition is still usable;
4. what the user can do, if action is required.

Bad:
> Something went wrong.

Good:
> Calendar sync failed, so today's edition was generated without calendar events. Printing continued. Reconnect the calendar connector before the next edition.
