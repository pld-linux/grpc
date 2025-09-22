# TODO:
# - system address_sorting and upb?
# - use shared grpc core in python modules
#
# Conditional build:
%bcond_without	apidocs		# (Python) API docs build
%bcond_without	python3		# CPython 3.x module
%bcond_without	systemd		# systemd support
#
Summary:	RPC library and framework
Summary(pl.UTF-8):	Biblioteka i szkielet RPC
Name:		grpc
Version:	1.75.0
Release:	1
License:	Apache v2.0
Group:		Libraries
#Source0Download: https://github.com/grpc/grpc/releases
Source0:	https://github.com/grpc/grpc/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	0b6c7ec8b62e9a71107b5f5bd12ef1a6
Source1:	https://github.com/census-instrumentation/opencensus-proto/archive/v0.3.0/opencensus-proto-0.3.0.tar.gz
# Source1-md5:	0b208800a68548cbf2d4bff763c050a2
Patch0:		python-deps.patch
URL:		https://grpc.io/
BuildRequires:	abseil-cpp-devel >= 20220623
BuildRequires:	c-ares-devel >= 1.13.0
BuildRequires:	cmake >= 3.16
BuildRequires:	gcc >= 6:4.7
BuildRequires:	libstdc++-devel >= 6:7
BuildRequires:	openssl-devel
BuildRequires:	pkgconfig
BuildRequires:	protobuf-devel >= 3.12
# with re2Config for cmake
BuildRequires:	re2-devel >= 20200801
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.714
%{?with_systemd:BuildRequires:	systemd-devel >= 1:233}
BuildRequires:	zlib-devel
%if %{with python3}
BuildRequires:	python3 >= 1:3.7
BuildRequires:	python3-Cython >= 3
BuildRequires:	python3-attrs
BuildRequires:	python3-modules >= 1:3.7
BuildRequires:	python3-setuptools
%endif
%if %{with apidocs}
BuildRequires:	python3-Sphinx >= 1.8.1
BuildRequires:	python3-six >= 1.10
%endif
%ifarch %{ix86}
Requires:	cpuinfo(sse2)
%endif
%{?with_systemd:Requires:	systemd-libs >= 1:233}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# Libs rquire non-function grpc_core::ExecCtx::exec_ctx_ and grpc_core::ApplicationCallbackExecCtx::callback_exec_ctx_ symbols.
# Wildcard '+' chars to workaround escape incompatibilities between rpm versions.
%define		skip_post_check_so	libgrpc...so.* libgrpc.._channelz.so.* libgrpc.._reflection.so.* libgrpc.._unsecure.so.*

%description
gRPC is a modern, open source, high-performance remote procedure call
(RPC) framework that can run anywhere. gRPC enables client and server
applications to communicate transparently, and simplifies the building
of connected systems.

%description -l pl.UTF-8
gRPC to nowoczesny, mający otwarty źródła, wydajny szkielet zdalnych
wywołań procedur (RPC - Remote Procedure Call). Pozwala na
przezroczystą komunikację klienta i serwera, upraszcza tworzenie
systemów połączonych.

%package devel
Summary:	Header files for gRPC library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki gRPC
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	c-ares-devel >= 1.13.0
Requires:	re2-devel >= 20200801
Requires:	zlib-devel

%description devel
Header files for gRPC library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki gRPC.

%package apidocs
Summary:	API documentation for gRPC library
Summary(pl.UTF-8):	Dokumentacja API biblioteki gRPC
Group:		Documentation
BuildArch:	noarch

%description apidocs
API documentation for gRPC library.

%description apidocs -l pl.UTF-8
Dokumentacja API biblioteki gRPC.

%package -n python3-grpcio
Summary:	HTTP/2 based RPC framework
Summary(pl.UTF-8):	Szkielet RPC oparty na HTTP/2
Group:		Libraries/Python

%description -n python3-grpcio
gRPC is a modern, open source, high-performance remote procedure call
(RPC) framework that can run anywhere. gRPC enables client and server
applications to communicate transparently, and simplifies the building
of connected systems.

%description -n python3-grpcio -l pl.UTF-8
gRPC to nowoczesny, mający otwarty źródła, wydajny szkielet zdalnych
wywołań procedur (RPC - Remote Procedure Call). Pozwala na
przezroczystą komunikację klienta i serwera, upraszcza tworzenie
systemów połączonych.

%package -n python3-grpcio-apidocs
Summary:	API documentation for Python gRPC library
Summary(pl.UTF-8):	Dokumentacja API biblioteki Pythona gRPC
Group:		Documentation
BuildArch:	noarch

%description -n python3-grpcio-apidocs
API documentation for Python gRPC library.

%description -n python3-grpcio-apidocs -l pl.UTF-8
Dokumentacja API biblioteki Pythona gRPC.

%prep
%setup -q
%patch -P0 -p1

%{__rm} doc/.gitignore

# simulate download_archive result
%{__tar} xf %{SOURCE1} -C third_party/opencensus-proto --strip-components=1 opencensus-proto-0.3.0/src

%build
install -d build
cd build
%cmake .. \
	-DCMAKE_CXX_STANDARD=17 \
	-DgRPC_INSTALL_CMAKEDIR:PATH=%{_lib}/cmake/grpc \
	-DgRPC_INSTALL_LIBDIR:PATH=%{_lib} \
	-DgRPC_ABSL_PROVIDER=package \
	-DgRPC_CARES_PROVIDER=package \
	-DgRPC_PROTOBUF_PROVIDER=package \
	-DgRPC_RE2_PROVIDER=package \
	-DgRPC_SSL_PROVIDER=package \
	-DgRPC_ZLIB_PROVIDER=package \
	-DgRPC_DOWNLOAD_ARCHIVES:BOOL=OFF \
	-DgRPC_USE_SYSTEMD:BOOL=%{__ON_OFF systemd}

%{__make}
cd ..

export GRPC_PYTHON_BUILD_SYSTEM_ABSL=1
export GRPC_PYTHON_BUILD_SYSTEM_CARES=1
export GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
export GRPC_PYTHON_BUILD_SYSTEM_RE2=1
export GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1
export GRPC_PYTHON_CFLAGS="-std=c++17 -fvisibility=hidden -fno-wrapv -fno-exceptions"

%if %{with python3}
%if %{with apidocs}
export GRPC_PYTHON_ENABLE_DOCUMENTATION_BUILD=1
%endif
%py3_build
%endif

%if %{with apidocs}
sphinx-build-3 -b html doc/python/sphinx doc/python/sphinx/_build/html
%endif

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

export GRPC_PYTHON_BUILD_SYSTEM_ABSL=1
export GRPC_PYTHON_BUILD_SYSTEM_CARES=1
export GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
export GRPC_PYTHON_BUILD_SYSTEM_RE2=1
export GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1
export GRPC_PYTHON_CFLAGS="-std=c++17 -fvisibility=hidden -fno-wrapv -fno-exceptions"

%if %{with python3}
%py3_install
%endif

install -d $RPM_BUILD_ROOT%{_docdir}
cp -pr doc $RPM_BUILD_ROOT%{_docdir}/%{name}-apidocs-%{version}
%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/%{name}-apidocs-%{version}/python/sphinx

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS CONCEPTS.md MAINTAINERS.md NOTICE.txt README.md TROUBLESHOOTING.md
%attr(755,root,root) %{_bindir}/grpc_cpp_plugin
%attr(755,root,root) %{_bindir}/grpc_csharp_plugin
%attr(755,root,root) %{_bindir}/grpc_node_plugin
%attr(755,root,root) %{_bindir}/grpc_objective_c_plugin
%attr(755,root,root) %{_bindir}/grpc_php_plugin
%attr(755,root,root) %{_bindir}/grpc_python_plugin
%attr(755,root,root) %{_bindir}/grpc_ruby_plugin
%attr(755,root,root) %{_libdir}/libgpr.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgpr.so.50
%attr(755,root,root) %{_libdir}/libgrpc.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc.so.50
%attr(755,root,root) %{_libdir}/libgrpc_authorization_provider.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc_authorization_provider.so.1.75
%attr(755,root,root) %{_libdir}/libgrpc_plugin_support.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc_plugin_support.so.1.75
%attr(755,root,root) %{_libdir}/libgrpc_unsecure.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc_unsecure.so.50
%attr(755,root,root) %{_libdir}/libgrpc++.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc++.so.1.75
%attr(755,root,root) %{_libdir}/libgrpc++_alts.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc++_alts.so.1.75
%attr(755,root,root) %{_libdir}/libgrpc++_error_details.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc++_error_details.so.1.75
%attr(755,root,root) %{_libdir}/libgrpc++_reflection.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc++_reflection.so.1.75
%attr(755,root,root) %{_libdir}/libgrpc++_unsecure.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpc++_unsecure.so.1.75
%attr(755,root,root) %{_libdir}/libgrpcpp_channelz.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgrpcpp_channelz.so.1.75
# TODO: use system libs instead
%attr(755,root,root) %{_libdir}/libaddress_sorting.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libaddress_sorting.so.50
%attr(755,root,root) %{_libdir}/libupb_*.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libupb_*.so.50
# TODO: use system libs instead
%attr(755,root,root) %ghost %{_libdir}/libutf8_range_lib.so.50
%attr(755,root,root) %{_libdir}/libutf8_range_lib.so.*.*.*
%{_datadir}/grpc

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libgpr.so
%attr(755,root,root) %{_libdir}/libgrpc.so
%attr(755,root,root) %{_libdir}/libgrpc_authorization_provider.so
%attr(755,root,root) %{_libdir}/libgrpc_plugin_support.so
%attr(755,root,root) %{_libdir}/libgrpc_unsecure.so
%attr(755,root,root) %{_libdir}/libgrpc++.so
%attr(755,root,root) %{_libdir}/libgrpc++_alts.so
%attr(755,root,root) %{_libdir}/libgrpc++_error_details.so
%attr(755,root,root) %{_libdir}/libgrpc++_reflection.so
%attr(755,root,root) %{_libdir}/libgrpc++_unsecure.so
%attr(755,root,root) %{_libdir}/libgrpcpp_channelz.so
%attr(755,root,root) %{_libdir}/libaddress_sorting.so
%attr(755,root,root) %{_libdir}/libupb_*.so
%attr(755,root,root) %{_libdir}/libutf8_range_lib.so
%{_includedir}/grpc
%{_includedir}/grpc++
%{_includedir}/grpcpp
%{_libdir}/cmake/grpc
%{_pkgconfigdir}/gpr.pc
%{_pkgconfigdir}/grpc.pc
%{_pkgconfigdir}/grpc_unsecure.pc
%{_pkgconfigdir}/grpc++.pc
%{_pkgconfigdir}/grpc++_unsecure.pc
%{_pkgconfigdir}/grpcpp_otel_plugin.pc

%files apidocs
%defattr(644,root,root,755)
%{_docdir}/%{name}-apidocs-%{version}

%if %{with python3}
%files -n python3-grpcio
%defattr(644,root,root,755)
%dir %{py3_sitedir}/grpc
%{py3_sitedir}/grpc/*.py
%{py3_sitedir}/grpc/__pycache__
%dir %{py3_sitedir}/grpc/_cython
%attr(755,root,root) %{py3_sitedir}/grpc/_cython/cygrpc.cpython-*.so
%{py3_sitedir}/grpc/_cython/__init__.py
%{py3_sitedir}/grpc/_cython/__pycache__
%{py3_sitedir}/grpc/_cython/_credentials
%{py3_sitedir}/grpc/_cython/_cygrpc
%{py3_sitedir}/grpc/aio
%{py3_sitedir}/grpc/beta
%{py3_sitedir}/grpc/experimental
%{py3_sitedir}/grpc/framework
%{py3_sitedir}/grpcio-%{version}-py*.egg-info
%endif

%if %{with apidocs}
%files -n python3-grpcio-apidocs
%defattr(644,root,root,755)
%doc doc/python/sphinx/_build/html/{_static,*.html,*.js}
%endif
