Name:       glib2

%define keepstatic 1

Summary:    A library of handy utility functions
Version:    2.56.1
Release:    1
Group:      System/Libraries
License:    LGPLv2+
URL:        http://www.gtk.org
Source0:    %{name}-%{version}.tar.xz
Source2:    glib2.sh
Source3:    glib2.csh
Source4:    %{name}-rpmlintrc
Patch1:     0001-Add-dev-mmcblk-to-the-list-of-devices-to-be-detected.patch
Patch2:     glib-replace-some-criticals-with-warnings.patch
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
BuildRequires:  pkgconfig(libpcre)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(libffi)
BuildRequires:  gettext
BuildRequires:  glibc-devel
BuildRequires:  libattr-devel
BuildRequires:  python >= 2.5

%description
GLib is the low-level core library that forms the basis
for projects such as GTK+ and GNOME. It provides data structure
handling for C, portability wrappers, and interfaces for such runtime
functionality as an event loop, threads, dynamic loading, and an
object system.

This package provides version 2 of GLib.


%package static
Summary:    A library of handy utility functions
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}
Requires:   %{name}-devel = %{version}

%description static
The glib2-static package includes static libraries
of version 2 of the GLib library.


%package devel
Summary:    A library of handy utility functions
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}
Requires:   python

%description devel
The glib2-devel package includes the header files for
version 2 of the GLib library.


%prep
%setup -q -n %{name}-%{version}/upstream

# 0001-Add-dev-mmcblk-to-the-list-of-devices-to-be-detected.patch
%patch1 -p1
# glib-replace-some-criticals-with-warnings.patch
%patch2 -p1

%build
#
# First, build glib enabled for generating the Profile Guided Optimization
# metadata
#
%autogen  \
    --enable-static \
    --with-pcre=system \
    --disable-libmount

make %{?_smp_mflags}

cd tests/gobject

#
# Now run the glib performance tests to create the profile data
#
make performance CFLAGS="$CFLAGS -pg -fprofile-generate"
cd ../..
tests/gobject/performance type-check
rm `find -name "*.lo"`
rm `find -name "*.o"`
#
# And now compile again, using the generated profile data
#
make %{?_smp_mflags} CFLAGS="$CFLAGS -fprofile-use"

%install
rm -rf %{buildroot}
%make_install

## glib2.sh and glib2.csh
mkdir -p %{buildroot}%{_sysconfdir}/profile.d
install -p -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/profile.d
install -p -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/profile.d

rm -f %{buildroot}%{_libdir}/*.la
rm -f %{buildroot}%{_libdir}/gio/modules/*.{a,la}
rm -f %{buildroot}%{_datadir}/glib-2.0/codegen/*.{pyc,pyo}

# MeeGo does not provide bash completion
rm -rf %{buildroot}%{_sysconfdir}/bash_completion.d
rm -rf %{buildroot}%{_datadir}/bash-completion

%find_lang glib20
mv glib20.lang glib2.lang

%docs_package

%lang_package

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc COPYING
%{_libdir}/libglib-2.0.so.*
%{_libdir}/libgthread-2.0.so.*
%{_libdir}/libgmodule-2.0.so.*
%{_libdir}/libgobject-2.0.so.*
%{_libdir}/libgio-2.0.so.*
%{_sysconfdir}/profile.d/*
%dir %{_libdir}/gio
%dir %{_libdir}/gio/modules
%{_bindir}/gio-querymodules
%{_bindir}/glib-compile-schemas
%{_bindir}/gsettings
%{_bindir}/gdbus
%{_bindir}/glib-compile-resources
%{_bindir}/gresource
%{_bindir}/gapplication
%{_bindir}/gio
%{_datarootdir}/gettext/its

%files static
%defattr(-,root,root,-)
%defattr(-, root, root, -)
%{_libdir}/lib*.a

%files devel
%defattr(-,root,root,-)
%defattr(-, root, root, -)
%{_libdir}/lib*.so
%{_libdir}/glib-2.0
%{_includedir}/*
%{_datadir}/aclocal/*
%{_libdir}/pkgconfig/*
%{_datadir}/glib-2.0
%{_datadir}/gdb/auto-load/usr/lib/*.py*
%{_bindir}/glib-genmarshal
%{_bindir}/glib-gettextize
%{_bindir}/glib-mkenums
%{_bindir}/gobject-query
%{_bindir}/gtester
%{_bindir}/gdbus-codegen
%attr (0755, root, root) %{_bindir}/gtester-report
