Name:       glib2
Summary:    A library of handy utility functions
Version:    2.82.4
Release:    1
License:    LGPLv2+
URL:        http://www.gtk.org
Source0:    %{name}-%{version}.tar.bz2
Source1:    %{name}-rpmlintrc
Source2:    glib2.sh
Source3:    glib2.csh
Patch1:     0001-detect-removable-storage-properly.-JB-48442.patch
Patch2:     0002-glib-Replace-g_critical-in-g_source_remove-with-g_wa.patch
Patch3:     0003-gdbus-Use-DBUS_SESSION_BUS_ADDRESS-if-AT_SECURE-but-.patch
Patch4:     0004-Cope-with-timed-having-one-extra-level-of-indirectio.patch
BuildRequires: chrpath
BuildRequires: gettext
BuildRequires: perl
BuildRequires: meson
BuildRequires: python3-devel
# for sys/inotify.h
BuildRequires: glibc-devel
BuildRequires: pkgconfig(gobject-introspection-1.0)
BuildRequires: libatomic
BuildRequires: libattr-devel
BuildRequires: libselinux-devel
# for sys/sdt.h
BuildRequires: pkgconfig(libelf)
BuildRequires: pkgconfig(libffi)
BuildRequires: pkgconfig(libpcre2-8)
BuildRequires: pkgconfig(zlib)
# for G_HAVE_ISO_VARARGS (and unused tests)
BuildRequires: libstdc++-devel
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig

# glib typelib files moved from gobject-introspection to glib2
#Conflicts: gobject-introspection < 1.79.1

%description
GLib is the low-level core library that forms the basis
for projects such as GTK+ and GNOME. It provides data structure
handling for C, portability wrappers, and interfaces for such runtime
functionality as an event loop, threads, dynamic loading, and an
object system.

This package provides version 2 of GLib.


%package static
Summary:    A library of handy utility functions
Requires:   %{name} = %{version}-%{release}
Requires:   %{name}-devel = %{version}
Requires:   pcre2-static
Requires:   libatomic-static

%description static
The glib2-static package includes static libraries
of version 2 of the GLib library.


%package devel
Summary:    A library of handy utility functions
Requires:   %{name} = %{version}-%{release}
Requires:   python3-base
# glib gir files moved from gobject-introspection-devel to glib2-devel
#Conflicts: gobject-introspection-devel < 1.79.1

%description devel
The glib2-devel package includes the header files for
version 2 of the GLib library.


%prep
%autosetup -p1 -n %{name}-%{version}/upstream

%build
# Bug 1324770: Also explicitly remove PCRE sources since we use --with-pcre=system
rm -f glib/pcre/*.[ch]
%meson \
    --default-library=both \
    -Ddtrace=disabled \
    -Dlibmount=disabled \
    -Dman-pages=disabled \
    -Dsysprof=disabled \
    -Dsystemtap=disabled

%meson_build

%install
%meson_install
# Since this is a generated .py file, set it to a known timestamp for
# better reproducibility.
# Also copy the timestamp for other .py files, because meson doesn't
# do this, see https://github.com/mesonbuild/meson/issues/5027.
touch -r gio/gdbus-2.0/codegen/config.py.in %{buildroot}%{_datadir}/glib-2.0/codegen/*.py
chrpath --delete %{buildroot}%{_libdir}/*.so

# Perform byte compilation manually to avoid issues with
# irreproducibility of the default invalidation mode, see
# https://www.python.org/dev/peps/pep-0552/ and
# https://bugzilla.redhat.com/show_bug.cgi?id=1686078
export PYTHONHASHSEED=0
%global __python %{__python3} %{buildroot}%{_datadir}

mv %{buildroot}%{_bindir}/gio-querymodules %{buildroot}%{_bindir}/gio-querymodules-%{__isa_bits}
sed -i -e "/^gio_querymodules=/s/gio-querymodules/gio-querymodules-%{__isa_bits}/" %{buildroot}%{_libdir}/pkgconfig/gio-2.0.pc

mkdir -p %{buildroot}%{_libdir}/gio/modules
touch %{buildroot}%{_libdir}/gio/modules/giomodule.cache

## glib2.sh and glib2.csh
mkdir -p %{buildroot}%{_sysconfdir}/profile.d
install -p -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/profile.d
install -p -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/profile.d

# Do not provide bash completion
rm -rf %{buildroot}%{_sysconfdir}/bash_completion.d
rm -rf %{buildroot}%{_datadir}/bash-completion

%find_lang glib20
mv glib20.lang glib2.lang

%transfiletriggerin -- %{_libdir}/gio/modules
gio-querymodules-%{__isa_bits} %{_libdir}/gio/modules &> /dev/null || :

%transfiletriggerpostun -- %{_libdir}/gio/modules
gio-querymodules-%{__isa_bits} %{_libdir}/gio/modules &> /dev/null || :

%transfiletriggerin -- %{_datadir}/glib-2.0/schemas
glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :

%transfiletriggerpostun -- %{_datadir}/glib-2.0/schemas
glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :

%lang_package

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%license LICENSES/LGPL-2.1-or-later.txt
%{_libdir}/libglib-2.0.so.*
%{_libdir}/libgthread-2.0.so.*
%{_libdir}/libgmodule-2.0.so.*
%{_libdir}/libgobject-2.0.so.*
%{_libdir}/libgio-2.0.so.*
%{_libdir}/libgirepository-2.0.so.0*
%dir %{_libdir}/girepository-1.0
%{_libdir}/girepository-1.0/GIRepository-3.0.typelib
%{_libdir}/girepository-1.0/GLib-2.0.typelib
%{_libdir}/girepository-1.0/GLibUnix-2.0.typelib
%{_libdir}/girepository-1.0/GModule-2.0.typelib
%{_libdir}/girepository-1.0/GObject-2.0.typelib
%{_libdir}/girepository-1.0/Gio-2.0.typelib
%{_libdir}/girepository-1.0/GioUnix-2.0.typelib
%dir %{_datadir}/glib-2.0
%dir %{_datadir}/glib-2.0/schemas
%dir %{_libdir}/gio
%dir %{_libdir}/gio/modules
%ghost %{_libdir}/gio/modules/giomodule.cache
%{_bindir}/gio
%{_bindir}/gio-querymodules*
%{_bindir}/glib-compile-schemas
%{_bindir}/gsettings
%{_bindir}/gdbus
%{_bindir}/gapplication
%{_libexecdir}/gio-launch-desktop
%{_sysconfdir}/profile.d/*

%files devel
%{_libdir}/lib*.so
%{_libdir}/glib-2.0
%{_includedir}/*
%{_datadir}/aclocal/*
%{_libdir}/pkgconfig/*
%{_datadir}/glib-2.0/
%{_datadir}/gdb/
%dir %{_datadir}/gir-1.0
%{_datadir}/gir-1.0/GIRepository-3.0.gir
%{_datadir}/gir-1.0/GLib-2.0.gir
%{_datadir}/gir-1.0/GLibUnix-2.0.gir
%{_datadir}/gir-1.0/GModule-2.0.gir
%{_datadir}/gir-1.0/GObject-2.0.gir
%{_datadir}/gir-1.0/Gio-2.0.gir
%{_datadir}/gir-1.0/GioUnix-2.0.gir
%{_datadir}/gettext/
%{_bindir}/glib-genmarshal
%{_bindir}/glib-gettextize
%{_bindir}/glib-mkenums
%{_bindir}/gi-compile-repository
%{_bindir}/gi-decompile-typelib
%{_bindir}/gi-inspect-typelib
%{_bindir}/gobject-query
%{_bindir}/gtester
%{_bindir}/gdbus-codegen
%{_bindir}/glib-compile-resources
%{_bindir}/gresource
%attr (0755, root, root) %{_bindir}/gtester-report

%files static
%{_libdir}/lib*.a
