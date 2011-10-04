#
# Please submit bugfixes or comments via http://bugs.meego.com/
#

%define libdir /%{_lib}

Name:           glib2
Version:        2.28.8
Release:        1
License:        LGPLv2+
Summary:        A library of handy utility functions
Url:            http://www.gtk.org
Group:          System/Libraries
Source0:        http://download.gnome.org/sources/glib/2.28/glib-%{version}.tar.bz2
Source1:        http://download.gnome.org/sources/glib/2.28/glib-%{version}.sha256sum
Source2:        glib2.sh
Source3:        glib2.csh
Source101:      %{name}-rpmlintrc

Patch1:         glib-2.24.0-syslog-message-handler.patch
Patch2:         glib-no-fsync.patch
BuildRequires:  gettext
# for sys/inotify.h
BuildRequires:  glibc-devel
BuildRequires:  libattr-devel
BuildRequires:  pkgconfig
BuildRequires:  gamin-devel
BuildRequires:  pkgconfig(libpcre)
BuildRequires:  pkgconfig(zlib)

%description
GLib is the low-level core library that forms the basis
for projects such as GTK+ and GNOME. It provides data structure
handling for C, portability wrappers, and interfaces for such runtime
functionality as an event loop, threads, dynamic loading, and an
object system.

This package provides version 2 of GLib.

%package devel
Summary:        A library of handy utility functions
Group:          Development/Libraries
Requires:       %{name} = %{version}
Requires:       pkgconfig

%description devel
The glib2-devel package includes the header files for
version 2 of the GLib library.

# anaconda needs static libs, see RH bug #193143
%package static
Summary:        A library of handy utility functions
Group:          Development/Libraries
Requires:       %{name}-devel = %{version}

%description static
The glib2-static package includes static libraries
of version 2 of the GLib library.

%prep
%setup -q -n glib-%{version}
%patch1 -p1
#patch2 -p1


%build
%configure --disable-gtk-doc --enable-static --with-runtime-libdir=../../%{_lib} --with-pcre=system

#
# First, build glib enabled for generating the Profile Guided Optimization
# metadata
#
make %{?_smp_mflags} CFLAGS="$CFLAGS -pg -fprofile-generate"

#
# Now run the glib performance tests to create the profile dta
#
cd tests/gobject
make performance CFLAGS="$CFLAGS -pg -fprofile-generate"
cd ../..
tests/gobject/performance type-check

#
# And now compile again, using the generated profile data
#
rm `find -name "*.lo"`
rm `find -name "*.o"`
make %{?_smp_mflags} CFLAGS="$CFLAGS -fprofile-use"

%install

make DESTDIR=%{buildroot} install
## glib2.sh and glib2.csh
./mkinstalldirs %{buildroot}%{_sysconfdir}/profile.d
install -p -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/profile.d
install -p -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/profile.d

rm -f %{buildroot}%{_libdir}/*.la
rm -f %{buildroot}%{_libdir}/gio/modules/*.{a,la}

# MeeGo does not provide bash completion
rm -rf %{buildroot}%{_sysconfdir}/bash_completion.d

%find_lang glib20
mv glib20.lang glib2.lang

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%docs_package

%lang_package

%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING
%{libdir}/libglib-2.0.so.*
%{libdir}/libgthread-2.0.so.*
%{libdir}/libgmodule-2.0.so.*
%{libdir}/libgobject-2.0.so.*
%{libdir}/libgio-2.0.so.*
%{_sysconfdir}/profile.d/*
%dir %{_libdir}/gio
%dir %{_libdir}/gio/modules
%{_libdir}/gio/modules/libgiofam.so
%{_bindir}/gio-querymodules
%{_bindir}/glib-compile-schemas
%{_bindir}/gsettings
%{_bindir}/gdbus

%files devel
%defattr(-, root, root, -)
%{_libdir}/lib*.so
%{_libdir}/glib-2.0
%{_includedir}/*
%{_datadir}/aclocal/*
%{_libdir}/pkgconfig/*
%{_datadir}/glib-2.0
%{_datadir}/gdb/auto-load/lib/*.py*
%doc %{_datadir}/gtk-doc/html/*
%{_bindir}/glib-genmarshal
%{_bindir}/glib-gettextize
%{_bindir}/glib-mkenums
%{_bindir}/gobject-query
%{_bindir}/gtester
%attr (0755, root, root) %{_bindir}/gtester-report

%files static
%defattr(-, root, root, -)
%{_libdir}/lib*.a

