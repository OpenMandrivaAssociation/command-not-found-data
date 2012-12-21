
Name:           command-not-found
Version:        2012.12.21
Release:        1
Summary:        Data files for command-not-found
Group:          File tools
License:        GPLv2
URL:            N/A
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

%description
Contains data files for command-not-found tool.
This package will be rebuilt every week with new data.

%prep
%setup -q -n %{name}

%install
mkdir -p %{buildroot}/usr/share/command-not-found
cp data.json %{buildroot}/usr/share/command-not-found/data.json

%files
%dir /usr/share/command-not-found/
/usr/share/command-not-found/data.json
