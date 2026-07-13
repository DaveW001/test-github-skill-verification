/**
 * Gmail Markdown Export — Google Apps Script
 *
 * Exports Gmail messages for a date range as a markdown file saved to Google Drive.
 * Same format as scripts/export-gmail-window.py so the pre-triage pipeline works unchanged.
 *
 * HOW TO USE:
 * 1. Go to https://script.google.com/
 * 2. Click "New project"
 * 3. Delete any default code and paste this entire file
 * 4. Click the "Run" button (or ▶ icon) — grant permissions when prompted
 * 5. Check the Execution log for progress
 * 6. The markdown file will be saved to your Google Drive root as "gmail_export_90days.md"
 * 7. Download it from Drive to: C:\development\02-Kx-to-process\60 archive\2026-05-03\
 *
 * CONFIGURE: Edit START_DATE, END_DATE, and MAX_MESSAGES below.
 */

// === CONFIGURATION ===
var START_DATE = "2026/02/01";        // Start date (inclusive)
var END_DATE = "2026/05/01";          // End date (exclusive)
var MAX_MESSAGES = 500;               // Max messages to export (increase as needed)
var OUTPUT_FILENAME = "gmail_export_90days.md";
// =======================

function exportGmailToMarkdown() {
  Logger.log("Starting Gmail export...");
  Logger.log("Date range: " + START_DATE + " to " + END_DATE);

  // Build Gmail search query
  var query = "after:" + START_DATE + " before:" + END_DATE;
  Logger.log("Query: " + query);

  // Search for threads
  var threads = GmailApp.search(query, 0, MAX_MESSAGES);
  Logger.log("Found " + threads.length + " threads");

  var messages = [];
  var msgCount = 0;

  // Flatten threads into individual messages
  for (var t = 0; t < threads.length; t++) {
    var thread = threads[t];
    var threadMessages = thread.getMessages();
    for (var m = 0; m < threadMessages.length; m++) {
      var msg = threadMessages[m];
      var date = msg.getDate();

      // Check date is within range (Apps Script search can be imprecise)
      var startDate = new Date(START_DATE);
      var endDate = new Date(END_DATE);
      if (date >= startDate && date < endDate) {
        messages.push(msg);
        msgCount++;
      }

      // Respect max limit
      if (msgCount >= MAX_MESSAGES) break;
    }
    if (msgCount >= MAX_MESSAGES) break;

    if ((t + 1) % 50 === 0) {
      Logger.log("Processed " + (t + 1) + "/" + threads.length + " threads...");
    }
  }

  Logger.log("Total messages to export: " + messages.length);

  // Build markdown content
  var md = [];
  md.push("# Gmail Export — dave.witkin@scruminc.com");
  md.push("");
  md.push("**Window:** " + START_DATE + " through " + END_DATE + " exclusive");
  md.push("**Total messages:** " + messages.length);
  md.push("");
  md.push("---");
  md.push("");

  for (var i = 0; i < messages.length; i++) {
    var msg = messages[i];
    var section = formatMessage(i + 1, msg);
    md.push(section);

    if ((i + 1) % 50 === 0) {
      Logger.log("Formatted " + (i + 1) + "/" + messages.length + " messages...");
    }
  }

  var content = md.join("\n");

  // Save to Google Drive
  var file = DriveApp.createFile(OUTPUT_FILENAME, content, MimeType.PLAIN_TEXT);
  Logger.log("File saved to Google Drive: " + file.getName());
  Logger.log("File URL: " + file.getUrl());
  Logger.log("Download and move to: C:\\development\\02-Kx-to-process\\60 archive\\2026-05-03\\" + OUTPUT_FILENAME);

  // Also log a summary
  var skipCount = 0;
  var ingestCount = 0;
  for (var j = 0; j < messages.length; j++) {
    var subj = messages[j].getSubject().toLowerCase();
    if (subj.indexOf("newsletter") >= 0 || subj.indexOf("notification") >= 0 || subj.indexOf("receipt") >= 0) {
      skipCount++;
    } else {
      ingestCount++;
    }
  }
  Logger.log("Quick classification estimate: ~" + ingestCount + " potential signal, ~" + skipCount + " likely noise");
  Logger.log("Export complete!");
}

function formatMessage(n, msg) {
  var subject = msg.getSubject() || "(no subject)";
  var from = msg.getFrom() || "";
  var to = msg.getTo() || "";
  var cc = msg.getCc() || "";
  var date = msg.getDate();
  var body = getPlainBody(msg);
  var snippet = body.length > 200 ? body.substring(0, 200) + "..." : body;

  // Get thread ID (Apps Script doesn't expose raw Gmail threadId, so we generate one)
  var threadId = "thread-" + date.getTime() + "-" + n;

  // Format date as ISO 8601
  var isoDate = Utilities.formatDate(date, "UTC", "yyyy-MM-dd'T'HH:mm:ss'Z'");

  // Escape backticks in values
  from = from.replace(/`/g, "'");
  to = to.replace(/`/g, "'");
  cc = cc.replace(/`/g, "'");
  subject = subject.replace(/`/g, "'");

  var lines = [];
  lines.push("## " + n + ". " + subject);
  lines.push("");
  lines.push("| Field | Value |");
  lines.push("|-------|-------|");
  lines.push("| MessageId | `" + threadId + "` |");
  lines.push("| ThreadId | `" + threadId + "` |");
  lines.push("| InternalDate | `" + isoDate + "` |");
  lines.push("| From | `" + from + "` |");
  if (to) {
    lines.push("| To | `" + to + "` |");
  }
  if (cc) {
    lines.push("| Cc | `" + cc + "` |");
  }
  lines.push("| Labels | `INBOX` |");
  lines.push("| Snippet | `" + snippet + "` |");
  lines.push("");
  lines.push(body);
  lines.push("");
  lines.push("---");
  lines.push("");

  return lines.join("\n");
}

function getPlainBody(msg) {
  try {
    // Try plain text first
    var plainBody = msg.getPlainBody();
    if (plainBody && plainBody.trim().length > 0) {
      return plainBody.trim();
    }
  } catch (e) {
    // Fall through to HTML
  }

  try {
    // Fall back to HTML body, strip tags
    var htmlBody = msg.getBody();
    return stripHtml(htmlBody);
  } catch (e) {
    return "(no body)";
  }
}

function stripHtml(html) {
  // Simple HTML stripping for Apps Script (no DOM available)
  var text = html;

  // Remove script and style blocks
  text = text.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, "");
  text = text.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, "");

  // Replace common HTML entities
  text = text.replace(/&nbsp;/g, " ");
  text = text.replace(/&amp;/g, "&");
  text = text.replace(/&lt;/g, "<");
  text = text.replace(/&gt;/g, ">");
  text = text.replace(/&quot;/g, '"');
  text = text.replace(/&#39;/g, "'");

  // Replace <br> and <p> with newlines
  text = text.replace(/<br\s*\/?>/gi, "\n");
  text = text.replace(/<\/p>/gi, "\n\n");
  text = text.replace(/<p[^>]*>/gi, "");

  // Replace <div> with newlines
  text = text.replace(/<\/div>/gi, "\n");
  text = text.replace(/<div[^>]*>/gi, "");

  // Replace <li> with bullet points
  text = text.replace(/<li[^>]*>/gi, "\n- ");
  text = text.replace(/<\/li>/gi, "");

  // Remove all remaining HTML tags
  text = text.replace(/<[^>]+>/g, "");

  // Collapse multiple newlines
  text = text.replace(/\n{3,}/g, "\n\n");

  return text.trim();
}
