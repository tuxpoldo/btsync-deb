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
			  .SelectNodes("//*/body/main/div/div/article/div/div[1]/p/strong");

	var textNodes = versionsPage.DocumentNode
			  .SelectNodes("//*/body/main/div/div/article/div/div[1]");

	if (versionNodes == null || textNodes == null || textNodes.Count() == 0)
	{
		throw new Exception("Changelog format changed!");
	}

	var versions = versionNodes.Select(x => x.InnerText.Trim()).ToList();
	var nodes = RecurseTextNodes(textNodes[0]);
	var text = string.Join("\n", nodes);

	// Cleanup formating
	text = text
		.Replace(delimiter, "'")
		.Replace("&nbsp;", " ")
		.Replace("&quot;", "\"")
		.Replace("&ldquo;", "\"")
		.Replace("&rdquo;", "\"")
		.Replace("\n\n", "\n")
		.Replace("\u200B", "")
		.Replace("&#8203;", "")
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
	for (var i = 0; i < Math.Min(versions.Count, 5); i++)
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

public IEnumerable<string> RecurseTextNodes(HtmlNode node)
{
	if (node.ChildNodes.Count == 0)
	{
		yield return node.InnerText;
		yield break;
	}

	foreach (var child in node.ChildNodes)
	{
		foreach (var r in RecurseTextNodes(child))
		{
			yield return r;
		}
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

void Run(string exe, string args, string path = "")
{
  var settings = new ProcessSettings
  {
    Arguments = args,
    WorkingDirectory = path
  };
  var exitCode = StartProcess(exe, settings);
	if(exitCode != 0)
	{
		throw new Exception("Process did not succeed.");
	}
}

string PackageToPath(string package)
{
  return string.Format("./{0}", package);
}

void CleanDebianWorkspace(string package, params string[] arches)
{
  var path = PackageToPath(package);
  Run("debuild", "clean", path);
	DeleteFiles(string.Format("./{0}*.build", package));
	DeleteFiles(string.Format("./{0}*.changes", package));
	DeleteFiles(string.Format("./{0}*.deb", package));
	DeleteFiles(string.Format("./{0}*.dsc", package));
	DeleteFiles(string.Format("./{0}*.tar.gz", package));
}

void BuildDebianPackage(string package, params string[] arches)
{
	Information("Extracting source.");
	var extractOptions = string.Format("-c \"tar xvf {0}_*.orig.tar.gz -C ./\"", package);
	Run("bash", extractOptions, "./");

	var path = PackageToPath(package);
  foreach(var arch in arches)
  {
		Information(string.Format("Building for arch {0}.", arch));
		var options = (arch == "all")
									? "-uc -us -b"
									: "-uc -us -b -a" + arch;
    Run("debuild", options, path);
  }
}

void BuildDebianSrc(string package)
{
  var path = PackageToPath(package);
  Run(path + "/debian/rules", "get-orig-source", path);
  Run("debuild", "-S -sa -kFEF78709", path);
}
