#load "tools/functions.cake"
#addin "Cake.FileHelpers"

var target = Argument<string>("target", "Default");

const string syncChangeLog = "http://help.getsync.com/customer/portal/articles/1908959";
const string historyPath = @"btsync-core\debian\history\changelog";
const string changelogFile = @"btsync-core\debian\changelog";

Task("Update-Changelog")
    .Does(() =>
{
    var lastVersion = GetLastVersion(syncChangeLog);
    Information(string.Format("Last detected version {0}.", lastVersion.Version));

    var currentHistory = FileReadText(historyPath);
    if(!currentHistory.Contains(lastVersion.Version))
    {
    	Information("Updating history file.");
    	currentHistory = CreateHistoryChangelog(lastVersion) + currentHistory;
    	FileWriteText(historyPath, currentHistory);
    }
    else
    {
    	Information("History file is already up-to-date.");
    }

    var currentChangelog = FileReadText(changelogFile);
    if(!currentChangelog.Contains(lastVersion.Version))
    {
    	Information("Updating changelog file.");
    	currentChangelog = CreateChangelog(lastVersion) + currentChangelog;
    	FileWriteText(changelogFile, currentChangelog);
    }
    else
    {
    	Information("Changelog file is already up-to-date.");
    }
});

Task("Default")
    .IsDependentOn("Update-Changelog");

RunTarget(target);
