#load "tools/functions.cake"
#load "tools/objects.cake"
#addin "Cake.FileHelpers"

// --target Clean
var target = Argument<string>("target", "Default");
// --packages btsync-common,btsync-core,btsync-gui,btsync-user,btsync
var packageArgs = Argument<string>("packages", "btsync-core,btsync").Split(',');

var availablePackageProfiles = new List<PackageProfile>()
    {
      new PackageProfile {
        Name = "btsync-common",
        Arches = "i386 amd64 armel armhf powerpc".Split()
      },
      new PackageProfile {
        Name = "btsync-core",
        Arches = "i386 amd64 armel armhf".Split()
      },
      new PackageProfile {
        Name = "btsync-gui",
        Arches = "all".Split()
      },
      new PackageProfile {
        Name = "btsync-user",
        Arches = "all".Split()
      },
      new PackageProfile {
        Name = "btsync",
        Arches = "all".Split()
      }
    };

var packageProfiles = availablePackageProfiles
                      .Where(x => packageArgs.Contains(x.Name))
                      .ToList();

const string syncChangeLog = "http://help.getsync.com/hc/en-us/articles/206216855-Sync-2-x-change-log";
const string historyPath = "btsync-core/debian/history/changelog";
const string changelogFile = "btsync-core/debian/changelog";

Task("Update-Changelog")
    .Does(() =>
{
    var lastVersion = GetLastVersion(syncChangeLog);
    Information(string.Format("Last detected version {0}.", lastVersion.Version));

    var currentHistory = FileReadText(historyPath);
    if(!currentHistory.Split('\n').Any(x => x.StartsWith(lastVersion.Version)))
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
    if(!currentChangelog.Contains("(" + lastVersion.Version))
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

Task("Clean")
    .Does(() =>
{
    foreach(var package in packageProfiles)
    {
        Information(string.Format("Cleaning workspace of {0}.", package.Name));
        CleanDebianWorkspace(package.Name, package.Arches);
    }
});

Task("Build-Src")
    .IsDependentOn("Clean")
    .Does(() =>
{
    foreach(var package in packageProfiles)
    {
        Information(string.Format("Building source of {0}.", package.Name));
        BuildDebianSrc(package.Name);
    }
});

Task("Build-Deb")
    .IsDependentOn("Build-Src")
    .Does(() =>
{
    foreach(var package in packageProfiles)
    {
        Information(string.Format("Building Debian package for {0}.", package.Name));
        BuildDebianPackage(package.Name, package.Arches);
    }
});

Task("Default")
    .IsDependentOn("Update-Changelog");

RunTarget(target);
