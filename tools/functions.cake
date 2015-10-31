#reference "tools/HtmlAgilityPack/lib/Net45/HtmlAgilityPack.dll"
using HtmlAgilityPack;
using System.Text.RegularExpressions;

const string maintainer = "Mark Lopez (Authority) <m@silvenga.com>";

IEnumerable<Release> GetVersions(string url)
{
	const string delimiter = "`";

	var webClient = new HtmlWeb();
	var versionsPage = webClient.Load(url);

	var versionNodes = versionsPage.DocumentNode
			  .SelectNodes("//*[@id='support-main']/div/div[2]/div[2]/span/span/strong");

	var textNodes = versionsPage.DocumentNode
			  .SelectNodes("//*[@id='support-main']/div/div[2]/div[2]");

	if (versionNodes == null || textNodes == null)
	{
		throw new Exception("Changelog format changed!");
	}

	var versions = versionNodes.Select(x => x.InnerText.Trim()).ToList();
	var text = textNodes[0].InnerText;

	// Cleanup formating
	text = text
		.Replace(delimiter, "'")
		.Replace("&nbsp;", " ")
		.Replace("&quot;", "\"")
		.Replace("&ldquo;", "\"")
		.Replace("&rdquo;", "\"")
		.Replace("&#39;", "'");

	// Split on versions
	foreach (var version in versions)
	{
		text = Regex.Replace(text, string.Format("\n[\\w| ]*{0}", version), delimiter);
	}

	// And cleanup
	var logs = text
		.Split(delimiter[0])
		.Select(x => x.Trim())
		.Where(x => !string.IsNullOrWhiteSpace(x))
		.ToList();

	// Return version objects
	for (var i = 0; i < versions.Count; i++)
	{
		var version = versions[i];
		var body = logs[i];
		yield return new Release
		{
			Changes = body,
			Version = version
		};
	}
}


public Release GetLastVersion(string url)
{
	var lastVerson = GetVersions(url)
				.OrderByDescending(x => x.Version)
				.First();
	return lastVerson;
}

public string CreateHistoryChangelog(Release release)
{
	var changelog =
				string.Format("{0} ({1})", release.Version, DateTime.Today.ToString("MM-dd-yy"))
 				+ Environment.NewLine
 				+ Environment.NewLine
 				+ release.Changes
 				+ Environment.NewLine
 				+ Environment.NewLine;

	return changelog;
}

public string CreateChangelog(Release release)
{
	var changelog =
				string.Format("btsync-core ({0}-1.0) unstable; urgency=medium", release.Version)
				+ Environment.NewLine
				+ Environment.NewLine
				+ "  * Non-maintainer upload."
				+ Environment.NewLine
				+ "  * New upstream release."
				+ Environment.NewLine
				+ Environment.NewLine
				+ string.Format(" -- {0}  {1}", "Mark Lopez (Authority) <m@silvenga.com>", DateTime.Now.ToString("ddd, dd MMM yyyy HH:mm:ss zz00"))
				+ Environment.NewLine
				+ Environment.NewLine;

	return changelog;
}

int Run(string exe, string args, string path = null)
{
  var settings = new ProcessSettings
  {
    Arguments = args,
    WorkingDirectory = path
  };
  return StartProcess(exe, settings);
}

string PackageToPath(string package)
{
  return string.Format("./{0}", package);
}

void CleanDebianWorkspace(string package, params string[] arches)
{
  var path = PackageToPath(package);
  Run("debuild", "clean", path);
  foreach(var arch in arches)
  {
		Information(string.Format("Cleaning for arch {0}.", arch));
    DeleteFiles(string.Format("./*{0}.build", arch));
    DeleteFiles(string.Format("./*{0}.changes", arch));
  }
}

void BuildDebianPackage(string package, params string[] arches)
{
  var path = PackageToPath(package);
  foreach(var arch in arches)
  {
		Information(string.Format("Building for arch {0}.", arch));
    Run("debuild", "-uc -us -b -a" + arch, path);
  }
}

void BuildDebianSrc(string package)
{
  var path = PackageToPath(package);
  Run("debian/rules", "get-orig-source", path);
  Run("debuild", "-S -sa -kFEF78709", path);
}
