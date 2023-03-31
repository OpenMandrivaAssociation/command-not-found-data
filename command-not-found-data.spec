Name:		command-not-found-data
Version:	2017
Release:	4
Summary:	Data files for command-not-found
Group:		File tools
License:	GPLv2
URL:		https://github.com/OpenMandrivaAssociation/command-not-found-data
Source0:	%{name}-%{version}.tar.xz
BuildArch:	noarch

%description
Contains data files for command-not-found tool.
This package will be rebuilt every week with new data.

%prep
%autosetup -n %{name} -p1

%install
mkdir -p %{buildroot}%{_datadir}/command-not-found
cp data.json %{buildroot}%{_datadir}/command-not-found/data.json

%files
%dir %{_datadir}/command-not-found
%{_datadir}/command-not-found/data.json
