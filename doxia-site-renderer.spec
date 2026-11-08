Name:		doxia-site-renderer
Version:	2.1.0
Release:	1
Summary:	Doxia site renderer
Group:		Development/Java
License:	ASL 2.0
URL:		https://maven.apache.org/doxia/doxia-sitetools/
Source0:	https://github.com/apache/maven-doxia-sitetools/archive/refs/tags/doxia-sitetools-%{version}.tar.gz#/doxia-sitetools-%{version}.tar.gz
BuildArch:	noarch
BuildRequires:	python
BuildRequires:	mvn(org.apache.maven:maven-artifact)
BuildRequires:	mvn(com.google.inject:guice-parent:pom::)
BuildRequires:	mvn(org.slf4j:slf4j-parent:pom::)
BuildRequires:	mvn(org.codehaus.plexus:plexus-containers:pom::)
BuildRequires:	mvn(org.codehaus.plexus:plexus:pom::)
BuildRequires:	mvn(org.apache.maven:maven-parent:pom::)
BuildRequires:	mvn(org.apache.commons:commons-parent:pom::)
BuildRequires:	mvn(org.slf4j:slf4j-api)
BuildRequires:	mvn(javax.inject:javax.inject)
BuildRequires:	mvn(org.apache.maven.doxia:doxia-core)
BuildRequires:	doxia-core >= 2.2.0
Requires:	doxia-core >= 2.2.0
BuildRequires:	mvn(org.apache.maven.doxia:doxia-sink-api)
BuildRequires:	doxia-sink-api >= 2.2.0
Requires:	doxia-sink-api >= 2.2.0
BuildRequires:	mvn(org.apache.maven.doxia:doxia-site-model)
BuildRequires:	doxia-site-model >= 2.1.0
Requires:	doxia-site-model >= 2.1.0
BuildRequires:	mvn(org.apache.maven.doxia:doxia-skin-model)
BuildRequires:	doxia-skin-model >= 2.1.0
Requires:	doxia-skin-model >= 2.1.0
BuildRequires:	mvn(org.apache.maven.doxia:doxia-module-xhtml5)
BuildRequires:	doxia-module-xhtml5 >= 2.2.0
Requires:	doxia-module-xhtml5 >= 2.2.0
BuildRequires:	mvn(org.eclipse.sisu:org.eclipse.sisu.plexus)
BuildRequires:	mvn(org.codehaus.plexus:plexus-velocity)
BuildRequires:	plexus-velocity >= 2.4.0
Requires:	plexus-velocity >= 2.4.0
BuildRequires:	mvn(org.codehaus.plexus:plexus-utils)
# 3.2.1 still provides the unversioned plexus-utils coordinate.
BuildRequires:	plexus-utils >= 3.6.2
Requires:	plexus-utils >= 3.6.2
BuildRequires:	mvn(org.apache.velocity:velocity-engine-core)
BuildRequires:	mvn(org.apache.velocity.tools:velocity-tools-generic)
BuildRequires:	mvn(org.apache.commons:commons-lang3)
# 3.3.2 still provides the unversioned commons-lang3 coordinate.
BuildRequires:	apache-commons-lang3 >= 3.21.0
Requires:	apache-commons-lang3 >= 3.21.0
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
Renders a Doxia document into a site, including Mermaid diagrams and
skin resources that match a condition. The XHTML5 parser is a compile
dependency because the renderer imports Xhtml5Sink. XML pull-parser
classes come from plexus-utils. PlexusContainer comes from Sisu.

%prep
%autosetup -n maven-doxia-sitetools-doxia-sitetools-%{version}
rm -rf src
mv doxia-site-renderer/src src
python - <<'PY'
import xml.etree.ElementTree as ET
NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)

def tag(name):
    return "{" + NS + "}" + name

def add(parent, name, text):
    node = ET.SubElement(parent, tag(name))
    node.text = text
    return node

root = ET.Element(tag("project"))
add(root, "modelVersion", "4.0.0")
add(root, "groupId", "org.apache.maven.doxia")
add(root, "artifactId", "doxia-site-renderer")
add(root, "version", "%{version}")
add(root, "name", "Doxia Sitetools :: Site Renderer")
props = ET.SubElement(root, tag("properties"))
add(props, "maven.compiler.release", "8")
add(props, "project.build.sourceEncoding", "UTF-8")
deps = ET.SubElement(root, tag("dependencies"))
for group, artifact, version, scope in (
    ("org.apache.maven", "maven-artifact", "3.10.0", "provided"),
    ("org.slf4j", "slf4j-api", "1.7.36", ""),
    ("javax.inject", "javax.inject", "1", ""),
    ("org.apache.maven.doxia", "doxia-core", "2.2.0", ""),
    ("org.apache.maven.doxia", "doxia-sink-api", "2.2.0", ""),
    ("org.apache.maven.doxia", "doxia-site-model", "2.1.0", ""),
    ("org.apache.maven.doxia", "doxia-skin-model", "2.1.0", ""),
    ("org.apache.maven.doxia", "doxia-module-xhtml5", "2.2.0", ""),
    ("org.eclipse.sisu", "org.eclipse.sisu.plexus", "0.9.0.M3", ""),
    ("org.codehaus.plexus", "plexus-velocity", "2.4.0", ""),
    ("org.codehaus.plexus", "plexus-utils", "3.6.2", ""),
    ("org.apache.velocity", "velocity-engine-core", "2.4.1", ""),
    ("org.apache.velocity.tools", "velocity-tools-generic", "3.1", ""),
    ("org.apache.commons", "commons-lang3", "3.21.0", ""),
):
    dep = ET.SubElement(deps, tag("dependency"))
    add(dep, "groupId", group)
    add(dep, "artifactId", artifact)
    add(dep, "version", version)
    if scope:
        add(dep, "scope", scope)
ET.ElementTree(root).write("pom.xml", encoding="utf-8", xml_declaration=True)
PY
# Sisu loads @Named classes from this index. The indexer plugin is not packaged.
python - <<'PY'
import re
from pathlib import Path
root = Path("src/main/java")
names = []
for path in sorted(root.rglob("*.java")):
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\b(?:class|interface|enum)\s+([A-Za-z0-9_]+)", text)
    if not match:
        continue
    if "@Named" not in text[:match.start()]:
        continue
    pkg = re.search(r"(?m)^package\s+([A-Za-z0-9_.]+)\s*;", text)
    if not pkg:
        continue
    names.append(pkg.group(1) + "." + match.group(1))
if names:
    dest = Path("src/main/resources/META-INF/sisu")
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "javax.inject.Named").write_text("\n".join(names) + "\n", encoding="utf-8")
PY
rm -rf doxia-integration-tools doxia-site-model doxia-site-renderer doxia-skin-model

%files -f .mfiles
%doc README.md
