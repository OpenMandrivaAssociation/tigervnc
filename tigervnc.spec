# snapshotver is year-month-day-svnrevision, generated by "make dist"
%define snapshot        1
%define snapshotversion 201103164362
%define version         1.0.90
%define rel             2

Name:    tigervnc
Version: %{version}
%if %{snapshot}
Release: %mkrel 0.%{snapshotversion}.%{rel}
%else
Release: %mkrel %{rel}
%endif

License:   GPLv2+
URL:       http://www.tigervnc.com/
Source0: %{name}-%{version}.tar.gz
Source1: vncviewer.desktop
# Missing from "make dist":
Source2: %{name}-media.tar.gz
# S3: combines 0001-Add-lcrypto-for-SHA1-functions.patch and the unix/xserver19.patch patch
Source3: tigervnc-1.0.90-xserver19.diff
# fedora patches
Patch0: tigervnc-102434.patch
Patch4: tigervnc-cookie.patch
Patch8: tigervnc-viewer-reparent.patch
Patch10: tigervnc11-ldnow.patch
Patch11: tigervnc11-gethomedir.patch
Patch12: tigervnc11-glx.patch
Patch13: tigervnc11-rh692048.patch
Patch14: 0001-Use-memmove-instead-of-memcpy-in-fbblt.c-when-memory.patch
Patch15: tigervnc11-CVE-2011-1775.patch
Patch16: tigervnc11-xorg111.patch

Patch50: 0001-Add-lcrypto-for-SHA1-functions.patch
BuildRequires: x11-server-source
BuildRequires: gettext-devel
BuildRequires: libx11-devel
BuildRequires: libxext-devel
BuildRequires: x11-font-util
BuildRequires: x11-util-macros
BuildRequires: x11-xtrans-devel
BuildRequires: mesagl-devel
BuildRequires: libxkbfile-devel
BuildRequires: libxfont-devel
BuildRequires: pixman-devel
BuildRequires: openssl-devel
BuildRequires: libpciaccess-devel
BuildRequires: libpam-devel
BuildRequires: libxtst-devel
BuildRequires: gnutls-devel
BuildRequires: imagemagick
BuildRequires: nasm
BuildRequires: java-devel

#------------------------------------------------------------------------------

# package tigervnc

Summary: Viewer for the VNC remote display system
Group:   Networking/Remote access

# Old RealVNC package:
Obsoletes: vnc
Provides:  vncviewer
Conflicts: tightvnc
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%description
Virtual Network Computing (VNC) is a remote display system which
allows you to view a computing 'desktop' environment not only on the
machine where it is running, but from anywhere on the Internet and
from a wide variety of machine architectures.  This package contains a
client which will allow you to connect to other desktops running a VNC
server.

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc unix/README
%{_bindir}/vncviewer
%{_iconsdir}/*
%{_datadir}/applications/*
%{_mandir}/man1/vncviewer.1*


#------------------------------------------------------------------------------

%package server

Summary: Server for the VNC remote display system
Group:   Networking/Remote access

# Old RealVNC package:
Obsoletes: vnc-server
Provides:  vnc-server
Conflicts: tightvnc-server

Requires: vnc-server-common

%description server
The VNC system allows you to access the same desktop from a wide
variety of platforms.  This package is a TigerVNC server, allowing
others to access the desktop on your machine.

%files server
%defattr(-,root,root,-)
%{_bindir}/vncconfig
%{_bindir}/vncpasswd
%{_bindir}/x0vncserver
%{_bindir}/Xvnc
%{_bindir}/vncserver
%{_mandir}/man1/Xvnc.1*
%{_mandir}/man1/vncpasswd.1*
%{_mandir}/man1/vncconfig.1*
%{_mandir}/man1/vncserver.1*
%{_mandir}/man1/x0vncserver.1*

#------------------------------------------------------------------------------

%package server-module

Summary: Xorg module for the VNC remote display system
Group:   Networking/Remote access

Provides: vnc-server-module

Requires: x11-server-xorg

%description server-module
This package contains libvnc.so module to X server, allowing others
to access the desktop on your machine.

%files server-module
%defattr(-,root,root,-)
%{_libdir}/xorg/modules/extensions/libvnc.so

#------------------------------------------------------------------------------

%package java

Summary: Java viewer for the VNC remote display system
Group:   Networking/Remote access

# Old RealVNC package:
Obsoletes: vnc-java
Provides:  vnc-java
Conflicts: tightvnc-java

# "TightVNC-specific" is not a typo, see the README file located inside the
# java source tree
%description java
This distribution is based on the standard VNC source and includes new
TightVNC-specific features and fixes, such as additional low-bandwidth
optimizations, major GUI improvements, and more.

There are three basic ways to use TigerVNC Java viewer:
  1. Running applet as part of TigerVNC server installation.
  2. Running applet hosted on a standalone Web server.
  3. Running the viewer as a standalone application.

%files java
%defattr(-,root,root)
%{_javadir}/*.jar
%{_datadir}/%{name}

#------------------------------------------------------------------------------

%prep
%setup -q -a2

%patch0 -p1 -b .102434
%patch4 -p1 -b .cookie
%patch8 -p1 -b .viewer-reparent
%patch10 -p1 -b .ldnow
%patch11 -p1 -b .gethomedir
%patch12 -p1 -b .glx
%patch13 -p1 -b .rh692048

cp -r /usr/share/x11-server-source/* unix/xserver
pushd unix/xserver
for all in `find . -type f -perm -001`; do
	chmod -x "$all"
done
%patch14 -p1 -b .memcpy
popd
patch -p1 -b --suffix .vnc < %{SOURCE3}

%patch15 -p0 -b .CVE-2011-1775
%patch16 -p1 -b .xorg111

%patch50 -p0

# Use newer gettext
sed -i 's/AM_GNU_GETTEXT_VERSION.*/AM_GNU_GETTEXT_VERSION([0.17])/' \
	configure.ac

%build
# Temporary build with -fno-omit-frame-pointer, it causes problems
export CFLAGS="$RPM_OPT_FLAGS -fno-omit-frame-pointer"
export CXXFLAGS="$CFLAGS"

autoreconf -fiv
%configure2_5x --disable-static --with-system-jpeg
%make

# XXX: I'm not sure this define is actually needed
# Need this for shared objects that reference X Server, or other modules symbols
%define _disable_ld_no_undefined 1
# Search for modules in extra_module_dir before the default path.
# This will allow fglrx to install its modified modules in more cleaner way.
%define extra_module_dir %{_libdir}/xorg/extra-modules

pushd unix/xserver
rm -f configure
autoreconf -fiv

# After the "--disable-config-hal", most options are just a paste from
# Mandriva's x11-server. We need to check what we can clean here (without
# reducing features)
%configure2_5x  --disable-xorg \
		--disable-xwin \
		--disable-xvfb \
		--disable-xnest \
		--disable-dmx \
		--disable-xfbdev \
		--disable-xephyr \
		--disable-kdrive \
		--disable-config-dbus \
		--disable-config-hal \
		--with-log-dir=%{_logdir} \
		--with-os-vendor="Mandriva" \
		--with-os-name="`echo \`uname -s -r\` | sed -e s'/ /_/g'`" \
		--with-vendor-web="http://qa.mandriva.com" \
		--with-extra-module-dir=%{extra_module_dir} \
		--enable-xwrapper \
		--enable-pam \
		--with-default-font-path="catalogue:%{_sysconfdir}/X11/fontpath.d"

%make
popd

# Build icons
pushd media
%make
popd

# Build java
pushd java/src/com/tigervnc/vncviewer
%make all
popd

%install
rm -rf %{buildroot}

%makeinstall_std

pushd unix/xserver/hw/vnc
%makeinstall_std
popd

# Install desktop stuff
mkdir -p %{buildroot}/%{_datadir}/icons/hicolor/{16x16,24x24,48x48}/apps

pushd media/icons
    for s in 16 24 48; do
	install -m644 tigervnc_$s.png %{buildroot}/%{_datadir}/icons/hicolor/${s}x$s/apps/tigervnc.png
    done
popd

mkdir %{buildroot}/%{_datadir}/applications
desktop-file-install \
	--dir %{buildroot}%{_datadir}/applications \
	%{_sourcedir}/vncviewer.desktop

%find_lang %{name} %{name}.lang

# remove unwanted files
rm -f  %{buildroot}/%{_libdir}/xorg/modules/extensions/libvnc.la


# java
install -d -m 755 %{buildroot}%{_javadir}
install -d -m 755 %{buildroot}%{_datadir}/%{name}/classes
pushd java/src/com/tigervnc/vncviewer
    make install INSTALL_DIR=%{buildroot}%{_datadir}/%{name}/classes \
    ARCHIVE=vncviewer-%{version}.jar
popd

pushd %{buildroot}%{_datadir}/%{name}/classes
    mv vncviewer-%{version}.jar %{buildroot}%{_javadir}
    ln -s %{_javadir}/vncviewer-%{version}.jar VncViewer.jar
popd

pushd %{buildroot}%{_javadir}
    ln -s vncviewer-%{version}.jar vncviewer.jar
    ln -s vncviewer-%{version}.jar VncViewer.jar
popd

%clean
rm -rf %{buildroot}
